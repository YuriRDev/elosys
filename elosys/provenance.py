"""Shared provenance/collection module — every source goes through here."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import time
from pathlib import Path

from curl_cffi import CurlError, requests

from .util import canonical_json, git_commit, now_utc

_TIMEOUT = 300
_RETRIES = 4
# Akamai blocks by TLS fingerprint; curl_cffi impersonate passes.
_BACKOFF = 5

_IMPERSONATE = "chrome"
_HEADERS = {"Accept": "*/*", "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"}


def sha256_file(path: str | Path, _buf: int = 1 << 20) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        while chunk := f.read(_buf):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def sha256_bytes(b: bytes) -> tuple[str, int]:
    return hashlib.sha256(b).hexdigest(), len(b)


def get_source(con: sqlite3.Connection, *, name: str, agency: str, type: str,
               base_url: str, legal_basis: str | None = None,
               notes: str | None = None) -> int:
    row = con.execute("SELECT id FROM source WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]
    cur = con.execute(
        "INSERT INTO source (name, agency, type, base_url, legal_basis, notes, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, agency, type, base_url, legal_basis, notes, now_utc()),
    )
    return int(cur.lastrowid)


def download(url: str, dest: str | Path) -> tuple[int, str | None]:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(_RETRIES):
        try:
            r = requests.get(url, stream=True, timeout=_TIMEOUT, headers=_HEADERS,
                             impersonate=_IMPERSONATE)
            status = r.status_code
            if status >= 500 or status == 429:
                raise CurlError(f"HTTP {status}")
            if status == 403:
                raise RuntimeError(
                    f"HTTP 403 for {url} — blocked by the source's bot filter even with "
                    f"browser impersonation. Download it in a real browser and drop the "
                    f"file into the tmp dir; the collector will ingest it from there."
                )
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
            return status, r.headers.get("Content-Type")
        except (CurlError, OSError) as e:
            last_error = e
            if attempt < _RETRIES - 1:
                time.sleep(_BACKOFF * (2 ** attempt))
    raise RuntimeError(f"failed to download {url}: {last_error}")


def record_collection(con: sqlite3.Connection, *, source_id: int, url: str,
                      file: str | Path, http_status: int | None,
                      content_type: str | None,
                      notes: str | None = None) -> tuple[int, bool]:
    sha, size = sha256_file(file)
    existing = con.execute(
        "SELECT id FROM collection WHERE url = ? AND payload_sha256 = ? ORDER BY id LIMIT 1",
        (url, sha),
    ).fetchone()
    if existing:
        return existing["id"], False

    cur = con.execute(
        "INSERT INTO collection (source_id, url, http_status, accessed_at, "
        " payload_sha256, size_bytes, content_type, collector_commit, notes) "
        "VALUES (:source_id, :url, :http_status, :accessed_at, "
        " :payload_sha256, :size_bytes, :content_type, :collector_commit, :notes)",
        {
            "source_id": source_id, "url": url, "http_status": http_status,
            "accessed_at": now_utc(), "payload_sha256": sha, "size_bytes": size,
            "content_type": content_type, "collector_commit": git_commit(), "notes": notes,
        },
    )
    return int(cur.lastrowid), True


def record_file(con: sqlite3.Connection, *, collection_id: int, filename: str,
                sha256: str, size: int) -> int:
    cur = con.execute(
        "INSERT OR IGNORE INTO collection_file (collection_id, filename, sha256, size_bytes) "
        "VALUES (?, ?, ?, ?)",
        (collection_id, filename, sha256, size),
    )
    # An ignored INSERT retains the connection's previous lastrowid.
    if cur.rowcount == 1:
        return int(cur.lastrowid)
    row = con.execute(
        "SELECT id FROM collection_file WHERE collection_id = ? AND filename = ?",
        (collection_id, filename),
    ).fetchone()
    return row["id"]


def record_parse(con: sqlite3.Connection, *, collection_id: int, parser_name: str,
                 parser_version: str, rows_extracted: int, rows_rejected: int,
                 collection_file_id: int | None = None) -> int:
    cur = con.execute(
        "INSERT INTO parse (collection_id, collection_file_id, parser_name, parser_commit, "
        " parser_version, rows_extracted, rows_rejected, run_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (collection_id, collection_file_id, parser_name, git_commit(),
         parser_version, rows_extracted, rows_rejected, now_utc()),
    )
    return int(cur.lastrowid)


def reset_source(con: sqlite3.Connection, source_name: str, data_tables: list[str]) -> None:
    row = con.execute("SELECT id FROM source WHERE name = ?", (source_name,)).fetchone()
    for table in data_tables:
        con.execute(f"DELETE FROM {table}")  # noqa: S608
    if row is not None:
        sid = row["id"]
        con.execute(
            "DELETE FROM parse WHERE collection_id IN "
            "(SELECT id FROM collection WHERE source_id = ?)", (sid,))
        con.execute(
            "DELETE FROM collection_file WHERE collection_id IN "
            "(SELECT id FROM collection WHERE source_id = ?)", (sid,))
        con.execute("DELETE FROM collection WHERE source_id = ?", (sid,))
    con.commit()


def manifest(con: sqlite3.Connection) -> dict:
    out: list[dict] = []
    for c in con.execute(
        "SELECT c.id, s.name AS source, c.url, c.http_status, c.accessed_at, "
        "       c.payload_sha256, c.size_bytes "
        "FROM collection c JOIN source s ON s.id = c.source_id ORDER BY c.id"
    ):
        files = [
            dict(f) for f in con.execute(
                "SELECT filename, sha256, size_bytes FROM collection_file "
                "WHERE collection_id = ? ORDER BY filename", (c["id"],)
            )
        ]
        row = {k: c[k] for k in c.keys() if k != "id"}
        row["files"] = files
        out.append(row)
    return {
        "generated_at": now_utc(),
        "collector_commit": git_commit(),
        "sources": out,
    }


def write_manifest(con: sqlite3.Connection, path: str | Path) -> Path:
    path = Path(path)
    path.write_text(json.dumps(manifest(con), indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path


def verify(con: sqlite3.Connection) -> list[dict]:
    mismatches: list[dict] = []
    for c in con.execute(
        "SELECT id, url, payload_sha256 FROM collection ORDER BY id"
    ):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            download(c["url"], tmp_path)
            got, _ = sha256_file(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)
        if got != c["payload_sha256"]:
            mismatches.append({"collection_id": c["id"], "url": c["url"],
                               "expected": c["payload_sha256"], "got": got})
    return mismatches


__all__ = [
    "sha256_file", "sha256_bytes", "get_source", "download", "record_collection",
    "record_file", "record_parse", "reset_source", "manifest", "write_manifest",
    "verify", "canonical_json",
]
