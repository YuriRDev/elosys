"""SQLite connection + schema application (see ADs/banco.md)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = Path(__file__).with_name("schema.sql")


def connect(path: str | Path, *, write: bool = False) -> sqlite3.Connection:
    if write:
        con = sqlite3.connect(str(path))
    else:
        con = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    if write:
        con.execute("PRAGMA journal_mode = WAL")
        con.execute("PRAGMA synchronous = NORMAL")
    else:
        con.execute("PRAGMA query_only = ON")
    return con


def create_schema(path: str | Path) -> None:
    con = sqlite3.connect(str(path))
    try:
        con.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
        _migrate(con)
        con.commit()
    finally:
        con.close()


_ADDED_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "signal": [("amount_cents", "INTEGER"), ("path_length", "INTEGER")],
}


def _migrate(con: sqlite3.Connection) -> None:
    for table, columns in _ADDED_COLUMNS.items():
        existing = {row[1] for row in con.execute(f"PRAGMA table_info({table})")}  # noqa: S608
        for name, decl in columns:
            if name not in existing:
                con.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")  # noqa: S608
