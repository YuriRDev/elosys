"""Downloads publish complete files without replacing cached data on failure."""

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from elosys import provenance


@pytest.fixture
def serve_download(monkeypatch):
    servers = []
    monkeypatch.setattr(provenance, "_BACKOFF", 0)

    def serve(responses):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                status, body, declared_length = responses[min(self.server.attempts, len(responses) - 1)]
                self.server.attempts += 1
                self.send_response(status)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Length", str(declared_length))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)
                self.wfile.flush()
                self.close_connection = True

            def log_message(self, format, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.attempts = 0
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        servers.append((server, thread))
        return f"http://127.0.0.1:{server.server_port}/fixture.zip", server

    yield serve

    for server, thread in servers:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize("cached", [False, True])
def test_interrupted_download_leaves_destination_unchanged(tmp_path, serve_download, cached):
    dest = tmp_path / "fixture.zip"
    if cached:
        dest.write_bytes(b"previous complete download")
    url, server = serve_download([(200, b"partial", 100)])

    with pytest.raises(RuntimeError, match="failed to download"):
        provenance.download(url, dest)

    if cached:
        assert dest.read_bytes() == b"previous complete download"
    else:
        assert not dest.exists()
    assert list(tmp_path.iterdir()) == ([dest] if cached else [])
    assert server.attempts == provenance._RETRIES


def test_download_retries_interruption_and_publishes_complete_payload(tmp_path, serve_download):
    dest = tmp_path / "downloads" / "fixture.zip"
    dest.parent.mkdir()
    dest.write_bytes(b"previous complete download")
    url, server = serve_download([(200, b"partial", 100), (200, b"complete payload", 16)])

    assert provenance.download(url, dest) == (200, "application/zip")

    assert dest.read_bytes() == b"complete payload"
    assert list(dest.parent.iterdir()) == [dest]
    assert server.attempts == 2


def test_blocked_download_preserves_cached_payload(tmp_path, serve_download):
    dest = tmp_path / "fixture.zip"
    dest.write_bytes(b"previous complete download")
    url, server = serve_download([(403, b"blocked", 7)])

    with pytest.raises(RuntimeError, match="HTTP 403"):
        provenance.download(url, dest)

    assert dest.read_bytes() == b"previous complete download"
    assert list(tmp_path.iterdir()) == [dest]
    assert server.attempts == 1
