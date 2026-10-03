"""elosys verify against a mocked download() (no network)."""

from __future__ import annotations

from pathlib import Path

import pytest

from elosys import provenance
from elosys.db import connect, create_schema
from elosys.provenance import get_source, record_collection, verify

_OK = "https://cdn.example/ok.zip"
_CHANGED = "https://cdn.example/changed.zip"
_DOWN = "https://cdn.example/down.zip"
_API = "https://api.example/cnpj/123"

_ORIGINAL = {_OK: b"ok", _CHANGED: b"before", _DOWN: b"down", _API: b"{}"}


@pytest.fixture
def con(tmp_path):
    path = tmp_path / "t.db"
    create_schema(path)
    con = connect(path, write=True)
    bulk = get_source(con, name="bulk", agency="X", type="csv", base_url="https://cdn.example")
    api = get_source(con, name="api", agency="X", type="api", base_url="https://api.example")
    for url, payload in _ORIGINAL.items():
        f = tmp_path / "payload"
        f.write_bytes(payload)
        record_collection(con, source_id=api if url == _API else bulk, url=url, file=f,
                          http_status=200, content_type=None)
    con.commit()
    yield con
    con.close()


def _fake_download(calls: list[str]):
    served = {_OK: b"ok", _CHANGED: b"after", _API: b"{}"}

    def fake(url: str, dest: str | Path):
        calls.append(url)
        if url not in served:
            raise RuntimeError(f"failed to download {url}: HTTP 429")
        Path(dest).write_bytes(served[url])
        return 200, None
    return fake


def test_reports_ok_changed_and_error_without_aborting(con, monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(provenance, "download", _fake_download(calls))

    status = {r["url"]: r["status"] for r in verify(con)}

    assert status == {_OK: "ok", _CHANGED: "changed", _DOWN: "error"}
    assert calls == [_OK, _CHANGED, _DOWN]


def test_error_keeps_message_and_has_no_hash(con, monkeypatch):
    monkeypatch.setattr(provenance, "download", _fake_download([]))

    down = next(r for r in verify(con) if r["url"] == _DOWN)

    assert down["got"] is None
    assert "HTTP 429" in down["error"]


def test_api_lookups_only_with_include_api(con, monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(provenance, "download", _fake_download(calls))
    monkeypatch.setattr(provenance.time, "sleep", lambda s: None)

    results = verify(con, include_api=True, api_delay_seconds=0)

    assert _API in calls
    assert next(r for r in results if r["url"] == _API)["status"] == "ok"
