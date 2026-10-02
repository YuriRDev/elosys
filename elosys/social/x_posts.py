"""Coleta de posts/replies do X de contas declaradas por candidatos ao TSE."""

from __future__ import annotations

import json
import re
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..log import RowCounter, get_logger, step
from ..provenance import get_source, sha256_bytes
from ..util import canonical_json, now_utc
from .apify import run_actor
from .lexicon import all_terms, build_queries

log = get_logger("elosys.social.x_posts")

NETWORK = "x"
DEFAULT_SINCE = "2019-01-01"
DEFAULT_MAX_ITEMS = 120
DEFAULT_MIN_WEIGHT = "baixa"
DEFAULT_BATCH_SIZE = 10
DEFAULT_WORKERS = 4


_RESERVED = {
    "about", "account", "analytics", "bookmarks", "compose", "developer",
    "download", "explore", "hashtag", "help", "home", "i", "intent", "jobs",
    "lists", "login", "messages", "notifications", "privacy", "rules", "search",
    "settings", "share", "signup", "tos", "verified",
}

_INTENT_RE = re.compile(
    r"(?:^|https?://(?:[a-z0-9_\-]+\.)?)(?:twitter\.com(?:\.br)?|x\.com)/intent/(?:user|follow|profile)[^?]*\?[^#]*\bscreen_name=@?([A-Za-z0-9_]{1,15})(?=[^A-Za-z0-9_]|$)",
    re.I,
)

_HANDLE_RE = re.compile(
    r"(?:^|(?:https?://)?(?:[a-z0-9_\-]+\.)?)(?:twitter\.com(?:\.br)?|x\.com)/(?:#!/)?@?([A-Za-z0-9_]{1,15})(?=[^A-Za-z0-9_]|$)",
    re.I,
)

_PURE_HANDLE_RE = re.compile(r"^@([A-Za-z0-9_]{1,15})$")


_SCOPES: dict[str, str] = {
    "federal": "(ph.office LIKE '%DEPUTADO FEDERAL%' OR ph.office LIKE '%SENADOR%')",
    "deputados": "ph.office LIKE '%DEPUTADO%'",
    "electeds": "1=1",
    "all": None,
}

SOURCE = dict(
    name="X/Twitter (via Apify apidojo/tweet-scraper)",
    agency="X Corp. (conteúdo público) / coleta via Apify",
    type="scraping",
    base_url="https://x.com/",
    legal_basis=(
        "Manifestações públicas de agentes e candidatos a cargo público em rede "
        "social aberta. As contas são as declaradas pelos próprios candidatos ao "
        "TSE (rede_social_candidato, Res. TSE 23.610/2019). Conteúdo coletado só "
        "de perfis públicos, texto apenas."
    ),
    notes="Conteúdo efêmero: não entra no manifest.json / elosys verify. A "
          "integridade é o payload cru + sha256 + retrieved_at em social_post "
          "(ver schema.sql e elosys/social/__init__.py).",
)


def _compile_lexicon() -> list[tuple[str, re.Pattern]]:
    out: list[tuple[str, re.Pattern]] = []
    for _cat, term, _w, _n in all_terms():
        t = term.lower()
        pat = re.compile(rf"\b{re.escape(t)}\b" if " " not in t else re.escape(t))
        out.append((t, pat))
    return out


def normalize_handle(raw: str | None) -> str | None:
    if not raw:
        return None

    # limpa espacos, quebras, caracteres invisiveis unicode e aspas
    clean = re.sub(r"[\u200b-\u200d\ufeff\xa0\s'\"<>`]", "", raw)
    if not clean:
        return None

    # declaracoes feitas apenas com @usuario
    pure = _PURE_HANDLE_RE.match(clean)
    if pure:
        h = pure.group(1).lower()
        return None if h in _RESERVED or h.isdigit() else h

    # links de intent/follow com o screen_name na querystring
    intent = _INTENT_RE.search(clean)
    if intent:
        h = intent.group(1).lower()
        return None if h in _RESERVED or h.isdigit() else h

    # urls comuns do twitter/x, com subdominios, hashbang legado ou link de tweet
    m = _HANDLE_RE.search(clean)
    if not m:
        return None

    h = m.group(1).lower()
    if h in _RESERVED or h.isdigit():
        return None

    return h


def run(
    con: sqlite3.Connection,
    *,
    scope: str = "federal",
    limit: int | None = None,
    handles: list[str] | None = None,
    min_weight: str = DEFAULT_MIN_WEIGHT,
    max_items: int = DEFAULT_MAX_ITEMS,
    since: str = DEFAULT_SINCE,
    refresh: bool = False,
    batch_size: int = DEFAULT_BATCH_SIZE,
    workers: int = DEFAULT_WORKERS,
) -> dict:
    if scope not in _SCOPES:
        raise ValueError(f"scope inválido: {scope} (use {', '.join(_SCOPES)})")
    source_id = get_source(con, **SOURCE)

    with step(log, "resolver handles declarados ao TSE"):
        targets = _resolve_targets(con, source_id, scope, handles)
    if not refresh:
        targets = [t for t in targets if t["status"] not in ("active", "empty")]
    if limit:
        targets = targets[:limit]

    per_account_queries = len(build_queries("x", min_weight=min_weight))
    batches = [targets[i:i + batch_size] for i in range(0, len(targets), batch_size)]
    log.info(
        "%s contas em %d lote(s) de até %d (scope=%s, min_weight=%s: %d termos → %d queries/conta, "
        "max_items=%d/conta, since=%s, %d workers)",
        f"{len(targets):,}", len(batches), batch_size, scope, min_weight, len(all_terms()),
        per_account_queries, max_items, since, workers,
    )

    lex = _compile_lexicon()
    by_status: dict[str, int] = {}
    posts_new = 0
    rc = RowCounter(log, "lotes concluídos", every=1)

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futs = {
            pool.submit(_fetch_batch, batch, min_weight, max_items, since): batch
            for batch in batches
        }
        for fut in as_completed(futs):
            batch = futs[fut]
            rc.tick()
            handles_in_batch = {t["handle"] for t in batch}
            try:
                run_id, items, flat_queries = fut.result()
            except Exception as e:  # noqa: BLE001
                log.warning("  lote (%d contas, @%s...): %s", len(batch), batch[0]["handle"], e)
                for t in batch:
                    _mark(con, t["id"], "error")
                    by_status["error"] = by_status.get("error", 0) + 1
                con.commit()
                continue

            per_handle: dict[str, list[dict]] = {h: [] for h in handles_in_batch}
            for item in items:
                if not isinstance(item, dict) or str(item.get("id")) in ("-1", "None", ""):
                    continue
                author = ((item.get("author") or {}).get("userName") or "").lower()
                if author in per_handle:
                    per_handle[author].append(item)

            for t in batch:
                got = per_handle[t["handle"]]
                n_new = 0
                for item in got:
                    idx = item.get("searchTermIndex")
                    mq = flat_queries[idx] if isinstance(idx, int) and 0 <= idx < len(flat_queries) else None
                    if _store_post(con, t["id"], run_id, t["handle"], item, lex, mq):
                        n_new += 1
                posts_new += n_new
                status = "active" if got else "empty"
                _mark(con, t["id"], status)
                by_status[status] = by_status.get(status, 0) + 1
            con.commit()
    rc.done()

    total_posts = con.execute("SELECT count(*) FROM social_post").fetchone()[0]
    total_accounts = con.execute(
        "SELECT count(*) FROM social_account WHERE last_crawled_at IS NOT NULL"
    ).fetchone()[0]
    summary = {
        "accounts_crawled_this_run": len(targets),
        "by_status": by_status,
        "posts_new_this_run": posts_new,
        "total_posts": total_posts,
        "total_accounts_crawled": total_accounts,
    }
    log.info("done: %s", summary)
    return summary


def _resolve_targets(
    con: sqlite3.Connection, source_id: int, scope: str, handles: list[str] | None
) -> list[dict]:
    if handles:
        wanted = {h.lstrip("@").lower() for h in handles}
        rows = con.execute(
            "SELECT sm.person_id, sm.url, sm.provenance_id FROM social_media sm WHERE sm.platform = 'x'"
        ).fetchall()
        picked: dict[str, dict] = {}
        for r in rows:
            h = normalize_handle(r["url"])
            if h in wanted and h not in picked:
                picked[h] = dict(r)
        for h in wanted:
            picked.setdefault(h, {"person_id": None, "url": None, "provenance_id": None})
        chosen = [(h, d) for h, d in picked.items()]
    else:
        where = "sm.platform = 'x'"
        join = ""
        cond = _SCOPES[scope]
        if cond is not None:
            join = "JOIN politician_history ph ON ph.person_id = sm.person_id"
            where += f" AND {cond} AND ph.result LIKE 'ELEITO%'"
        rows = con.execute(
            f"SELECT DISTINCT sm.person_id, sm.url, sm.provenance_id "  # noqa: S608
            f"FROM social_media sm {join} WHERE {where}"
        ).fetchall()
        picked = {}
        for r in rows:
            h = normalize_handle(r["url"])
            if h and h not in picked:
                picked[h] = dict(r)
        chosen = [(h, d) for h, d in picked.items()]

    chosen.sort(key=lambda x: x[0])
    out: list[dict] = []
    now = now_utc()
    for h, d in chosen:
        con.execute(
            "INSERT INTO social_account "
            "(person_id, network, handle, handle_declared, declared_provenance_id, source_id, "
            " status, first_seen_at) "
            "VALUES (?, ?, ?, ?, ?, ?, 'pending', ?) "
            "ON CONFLICT (network, handle) DO UPDATE SET "
            "  person_id = coalesce(social_account.person_id, excluded.person_id), "
            "  declared_provenance_id = coalesce(social_account.declared_provenance_id, "
            "                                    excluded.declared_provenance_id)",
            (d.get("person_id"), NETWORK, h, d.get("url"), d.get("provenance_id"), source_id, now),
        )
        row = con.execute(
            "SELECT id, handle, person_id, status, last_crawled_at FROM social_account "
            "WHERE network = ? AND handle = ?",
            (NETWORK, h),
        ).fetchone()
        out.append(dict(row))
    con.commit()
    return out


def _mark(con: sqlite3.Connection, account_id: int, status: str) -> None:
    if status == "error":
        con.execute("UPDATE social_account SET status = 'error' WHERE id = ?", (account_id,))
    else:
        con.execute(
            "UPDATE social_account SET status = ?, last_crawled_at = ? WHERE id = ?",
            (status, now_utc(), account_id),
        )


def _fetch_batch(
    batch: list[dict], min_weight: str, max_items: int, since: str
) -> tuple[str, list[dict], list[str]]:
    flat_queries: list[str] = []
    for t in batch:
        flat_queries.extend(
            build_queries(t["handle"], min_weight=min_weight,
                          extra=f"since:{since} -filter:retweets")
        )
    actor_input = {
        "searchTerms": flat_queries,
        "maxItems": max_items * len(batch),
        "sort": "Latest",
    }
    run_id, items = run_actor(actor_input, max_wait_seconds=2400)
    log.info("  lote @%s..+%d: %d itens brutos", batch[0]["handle"], len(batch) - 1, len(items))
    return run_id, items, flat_queries


def _first(item: dict, *keys: str):
    for k in keys:
        v = item.get(k)
        if v not in (None, "", []):
            return v
    return None


def _store_post(
    con: sqlite3.Connection, account_id: int, run_id: str, handle: str, item: dict,
    lex: list[tuple[str, re.Pattern]], matched_query: str | None,
) -> bool:
    external_id = _first(item, "id", "id_str", "tweetId", "rest_id")
    text = _first(item, "text", "full_text", "fullText", "rawContent", "content") or ""
    if not external_id or not text:
        return False
    external_id = str(external_id)

    is_reply = bool(_first(item, "isReply", "is_reply")) or item.get("inReplyToId") is not None
    is_quote = bool(_first(item, "isQuote", "is_quote", "quoted_tweet", "quotedTweet"))
    kind = "reply" if is_reply else ("quote" if is_quote else "post")

    low = text.lower()
    matched = sorted({term for term, pat in lex if pat.search(low)})

    raw = canonical_json(item).encode("utf-8")
    sha, _ = sha256_bytes(raw)

    cur = con.execute(
        "INSERT OR IGNORE INTO social_post "
        "(social_account_id, external_id, kind, lang, text, in_reply_to_external, reply_to_handle, "
        " posted_at, like_count, repost_count, reply_count, url, matched_terms, matched_query, "
        " apify_run_id, raw_json, raw_sha256, retrieved_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            account_id, external_id, kind,
            _first(item, "lang", "language"),
            text,
            _first(item, "inReplyToId", "in_reply_to_status_id_str", "conversationId"),
            _first(item, "inReplyToUsername", "in_reply_to_screen_name"),
            _first(item, "createdAt", "created_at", "date", "timestamp"),
            _first(item, "likeCount", "favorite_count", "likes"),
            _first(item, "retweetCount", "retweet_count", "reposts"),
            _first(item, "replyCount", "reply_count", "replies"),
            _first(item, "url", "twitterUrl", "tweetUrl")
            or f"https://x.com/{handle}/status/{external_id}",
            json.dumps(matched, ensure_ascii=False),
            matched_query,
            run_id,
            raw.decode("utf-8"),
            sha,
            now_utc(),
        ),
    )
    return cur.rowcount > 0


def stats(con: sqlite3.Connection) -> dict:
    out: dict = {}
    out["accounts"] = dict(
        con.execute(
            "SELECT status, count(*) FROM social_account GROUP BY status"
        ).fetchall()
    )
    out["posts_by_kind"] = dict(
        con.execute("SELECT kind, count(*) FROM social_post GROUP BY kind").fetchall()
    )
    out["posts_with_match"] = con.execute(
        "SELECT count(*) FROM social_post WHERE matched_terms != '[]'"
    ).fetchone()[0]
    return out


if __name__ == "__main__":
    for u in [
        "https://twitter.com/adriventurasp", "www.twitter.com/deputadoserafim",
        "https://x.com/adriana_accorsi?s=21&t=abc", "https://twitter.com/@motta_afonso",
        "http://www.twitter.com.br/draalehaber", "X.COM/ALCEU_ALCEUMOREIRA",
        "https://twitter.com/home", "https://instagram.com/foo",
        "https://twitter.com/#!/deputado_x", "@tabataamaralsp",
        "https://twitter.com/intent/user?screen_name=adriventurasp",
        "https://x.com/fulano/status/1800000000000000001",
    ]:
        print(f"{u:60} -> {normalize_handle(u)}")