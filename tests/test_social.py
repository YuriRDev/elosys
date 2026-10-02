"""social/x_posts + lexicon: handle normalization, query building, the local"""

from __future__ import annotations

import json

from elosys.db import connect, create_schema
from elosys.social import lexicon, x_posts

T = "2026-01-01T00:00:00Z"


def test_normalize_handle_variants():
    assert x_posts.normalize_handle("https://twitter.com/adriventurasp") == "adriventurasp"
    assert x_posts.normalize_handle("https://x.com/adriana_accorsi?s=21&t=abc") == "adriana_accorsi"
    assert x_posts.normalize_handle("http://www.twitter.com.br/DraAleHaber") == "draalehaber"
    assert x_posts.normalize_handle("https://twitter.com/@motta_afonso") == "motta_afonso"
    assert x_posts.normalize_handle("https://twitter.com/home") is None
    assert x_posts.normalize_handle("https://instagram.com/foo") is None
    assert x_posts.normalize_handle(None) is None

    # links legados com hashbang
    assert x_posts.normalize_handle("https://twitter.com/#!/deputado_x") == "deputado_x"
    assert x_posts.normalize_handle("http://x.com/#!/@senador_y") == "senador_y"

    # links de intent/follow com screen_name
    assert x_posts.normalize_handle("https://twitter.com/intent/user?screen_name=adriventurasp") == "adriventurasp"
    assert x_posts.normalize_handle("https://x.com/intent/follow?screen_name=@draalehaber") == "draalehaber"

    # links de tweet ou status colados pelo candidato
    assert x_posts.normalize_handle("https://x.com/fulano/status/1800000000000000001") == "fulano"
    assert x_posts.normalize_handle("https://twitter.com/fulano/statuses/1800000000000000001?s=20") == "fulano"

    # declaracao apenas com @usuario
    assert x_posts.normalize_handle("@tabataamaralsp") == "tabataamaralsp"

    # subdominios mobile e maiusculas
    assert x_posts.normalize_handle("mobile.twitter.com/deputado_z") == "deputado_z"
    assert x_posts.normalize_handle("www.x.com/@deputado_w") == "deputado_w"
    assert x_posts.normalize_handle("X.COM/ALCEU_ALCEUMOREIRA") == "alceu_alceumoreira"

    # espacos e caracteres invisiveis de copy-paste
    assert x_posts.normalize_handle("  https://x.com/fulano\u200b  ") == "fulano"
    assert x_posts.normalize_handle("<https://twitter.com/fulano/>") == "fulano"

    # rotas reservadas e nomes invalidos
    assert x_posts.normalize_handle("https://twitter.com/explore") is None
    assert x_posts.normalize_handle("https://twitter.com/search?q=tse") is None
    assert x_posts.normalize_handle("https://x.com/123456789") is None
    assert x_posts.normalize_handle("https://evil.com/twitter.com/fulano") is None


def test_lexicon_is_big_and_weighted():
    terms = lexicon.all_terms()
    assert len(terms) > 300
    weights = {w for _c, _t, w, _n in terms}
    assert weights == {"baixa", "media", "alta"}
    assert len(lexicon.search_terms("alta")) < len(lexicon.search_terms("baixa"))


def test_build_queries_shape():
    qs = lexicon.build_queries("fulano", min_weight="baixa")
    assert len(qs) > 1
    assert all(q.startswith("from:fulano (") for q in qs)
    assert all(len(q) <= 512 for q in qs)
    assert any('"ideologia de gênero"' in q for q in qs)


def test_compile_lexicon_word_boundary():
    lex = x_posts._compile_lexicon()
    pats = dict(lex)
    assert "foca" in pats
    assert pats["foca"].search("aquele deputado é uma foca")
    assert not pats["foca"].search("o processo foi para foragido")


def _seed_account(con):
    con.execute("INSERT INTO source (name, agency, type, base_url, created_at) "
                "VALUES ('X/Twitter','x','scraping','x',?)", (T,))
    con.execute("INSERT INTO social_account (network, handle, source_id, status, first_seen_at) "
                "VALUES ('x','fulano',1,'pending',?)", (T,))
    return con.execute("SELECT id FROM social_account").fetchone()["id"]


def test_store_post_writes_hash_and_matches(tmp_path):
    path = tmp_path / "t.db"
    create_schema(path)
    con = connect(path, write=True)
    acc = _seed_account(con)
    item = {
        "id": "1800000000000000001",
        "text": "esse cara é um viado, não merece respeito",
        "createdAt": "Tue Jun 18 16:32:24 +0000 2024",
        "lang": "pt",
        "isReply": False,
        "likeCount": 3,
        "author": {"userName": "fulano"},
        "url": "https://x.com/fulano/status/1800000000000000001",
    }
    lex = x_posts._compile_lexicon()
    assert x_posts._store_post(con, acc, "run1", "fulano", item, lex, "from:fulano (viado)")
    con.commit()

    row = con.execute("SELECT * FROM social_post").fetchone()
    assert row["kind"] == "post"
    assert row["external_id"] == "1800000000000000001"
    assert "viado" in json.loads(row["matched_terms"])
    assert len(row["raw_sha256"]) == 64
    assert row["apify_run_id"] == "run1"
    assert not x_posts._store_post(con, acc, "run2", "fulano", item, lex, None)