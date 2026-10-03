"""Repeated file registration must preserve the parser's original source."""

import pytest

from elosys.db import connect, create_schema
from elosys.provenance import get_source, record_collection, record_file, record_parse


@pytest.mark.parametrize("other_collection", [False, True])
def test_repeated_file_registration_keeps_correct_parse_source(tmp_path, other_collection):
    db_path = tmp_path / "provenance.db"
    create_schema(db_path)
    con = connect(db_path, write=True)
    try:
        source_id = get_source(
            con, name="Fixture", agency="Fixture", type="csv", base_url="https://example.invalid/",
        )
        payload = tmp_path / "fixture.csv"
        payload.write_bytes(b"fixture")
        collection_id, _ = record_collection(
            con, source_id=source_id, url="https://example.invalid/first",
            file=payload, http_status=200, content_type="text/csv",
        )
        first_id = record_file(
            con, collection_id=collection_id, filename="first.csv", sha256="a" * 64, size=1,
        )
        second_collection_id = collection_id
        if other_collection:
            second_collection_id, _ = record_collection(
                con, source_id=source_id, url="https://example.invalid/second",
                file=payload, http_status=200, content_type="text/csv",
            )
        record_file(
            con, collection_id=second_collection_id, filename="second.csv", sha256="b" * 64, size=2,
        )

        repeated_id = record_file(
            con, collection_id=collection_id, filename="first.csv", sha256="a" * 64, size=1,
        )
        parse_id = record_parse(
            con, collection_id=collection_id, collection_file_id=repeated_id,
            parser_name="fixture", parser_version="1", rows_extracted=1, rows_rejected=0,
        )

        source = con.execute(
            "SELECT f.id, f.collection_id, f.filename FROM parse p "
            "JOIN collection_file f ON f.id = p.collection_file_id WHERE p.id = ?",
            (parse_id,),
        ).fetchone()
        assert tuple(source) == (first_id, collection_id, "first.csv")
        assert con.execute("SELECT count(*) FROM collection_file").fetchone()[0] == 2
    finally:
        con.close()
