"""Read connections must not create databases or change their journal mode."""

import sqlite3

import pytest

from elosys.db import connect


def test_read_connection_does_not_create_missing_database(tmp_path):
    path = tmp_path / "missing.db"

    with pytest.raises(sqlite3.OperationalError):
        connect(path)

    assert not path.exists()
    assert list(tmp_path.iterdir()) == []


def test_read_connection_preserves_database_and_journal_mode(tmp_path):
    # URI metacharacters in filesystem paths must remain part of the filename.
    path = tmp_path / "dados #1 100%.db"
    with sqlite3.connect(path) as writer:
        writer.execute("CREATE TABLE fixture (value TEXT)")
        writer.execute("INSERT INTO fixture VALUES ('original')")
    writer.close()
    before = path.read_bytes()

    reader = connect(path)
    try:
        assert reader.execute("SELECT value FROM fixture").fetchone()["value"] == "original"
        assert reader.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
        with pytest.raises(sqlite3.OperationalError):
            reader.execute("INSERT INTO fixture VALUES ('changed')")
    finally:
        reader.close()

    assert path.read_bytes() == before
    assert list(tmp_path.iterdir()) == [path]


def test_write_connection_still_creates_wal_database(tmp_path):
    path = tmp_path / "writer.db"
    writer = connect(path, write=True)
    try:
        assert writer.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        writer.execute("CREATE TABLE fixture (value TEXT)")
        writer.execute("INSERT INTO fixture VALUES ('written')")
        writer.commit()
    finally:
        writer.close()

    reader = connect(path)
    try:
        assert reader.execute("SELECT value FROM fixture").fetchone()[0] == "written"
        assert reader.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.OperationalError):
            reader.execute("PRAGMA query_only = OFF")
            reader.execute("INSERT INTO fixture VALUES ('blocked')")
    finally:
        reader.close()
