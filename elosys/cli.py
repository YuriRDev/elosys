"""Elosys CLI — one independent crawler per data source (see ADs/imutabilidade.md)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .db import connect, create_schema
from .log import get_logger
from .provenance import verify, write_manifest
from .receita import cnpj as receita_cnpj
from .rules import (
    ai_review,
    candidate_supplier_partner,
    circular_donations,
    disproportionate_expense,
    social_review,
)
from .social import x_posts
from .transparencia import earmarks, sanctions
from .tse import accounts, assets, candidates, photo_urls, social

DEFAULT_TMP = "dados_tmp"
log = get_logger("elosys.cli")


def _init_db(args: argparse.Namespace) -> int:
    create_schema(args.db)
    log.info("schema applied to %s", args.db)
    return 0


def _run_crawler(args: argparse.Namespace, module, name: str) -> int:
    db = Path(args.db)
    create_schema(db)
    years = [int(y) for y in args.years.split(",")] if args.years else None
    con = connect(db, write=True)
    try:
        report = module.run(con, years=years, tmp_dir=args.tmp)
        write_manifest(con, db.with_name("manifest.json"))
    finally:
        con.close()
    report_path = db.with_name(f"{name}_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s and refreshed manifest.json — commit both", report_path.name)
    return 0


def _run_sanctions(args: argparse.Namespace) -> int:
    db = Path(args.db)
    create_schema(db)
    con = connect(db, write=True)
    try:
        report = sanctions.run(con, tmp_dir=args.tmp)
        write_manifest(con, db.with_name("manifest.json"))
    finally:
        con.close()
    report_path = db.with_name("transparencia_sanctions_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s and refreshed manifest.json — commit both", report_path.name)
    return 0


def _run_receita_cnpj(args: argparse.Namespace) -> int:
    db = Path(args.db)
    create_schema(db)
    con = connect(db, write=True)
    try:
        cnpjs = args.cnpjs.split(",") if args.cnpjs else None
        report = receita_cnpj.run(con, limit=args.limit, cnpjs=cnpjs, tmp_dir=args.tmp,
                                  order=args.order, include_campaign=args.include_campaign)
        write_manifest(con, db.with_name("manifest.json"))
    finally:
        con.close()
    report_path = db.with_name("receita_cnpj_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s and refreshed manifest.json — commit both", report_path.name)
    return 0


def _run_earmarks(args: argparse.Namespace) -> int:
    db = Path(args.db)
    create_schema(db)
    con = connect(db, write=True)
    try:
        report = earmarks.run(con, tmp_dir=args.tmp)
        write_manifest(con, db.with_name("manifest.json"))
    finally:
        con.close()
    report_path = db.with_name("transparencia_earmarks_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s and refreshed manifest.json — commit both", report_path.name)
    return 0


def _run_photo_urls(args: argparse.Namespace) -> int:
    db = Path(args.db)
    create_schema(db)
    con = connect(db, write=True)
    try:
        person_ids = [int(p) for p in args.person_ids.split(",")] if args.person_ids else None
        years = [int(y) for y in args.years.split(",")] if args.years else None
        report = photo_urls.run(con, limit=args.limit, person_ids=person_ids, years=years,
                                tmp_dir=args.tmp, workers=args.workers)
        write_manifest(con, db.with_name("manifest.json"))
    finally:
        con.close()
    report_path = db.with_name("tse_photo_urls_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s and refreshed manifest.json — commit both", report_path.name)
    return 0


def _run_rule(args: argparse.Namespace, module, name: str) -> int:
    db = Path(args.db)
    create_schema(db)
    con = connect(db, write=True)
    try:
        report = module.run(con)
    finally:
        con.close()
    report_path = db.with_name(f"{name}_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s", report_path.name)
    return 0


def _run_rule_circular_donations(args: argparse.Namespace) -> int:
    db = Path(args.db)
    create_schema(db)
    con = connect(db, write=True)
    try:
        report = circular_donations.run(con, max_depth=args.max_depth, max_fanout=args.max_fanout,
                                        min_amount_cents=round(args.min_amount_brl * 100))
    finally:
        con.close()
    report_path = db.with_name("rule_circular_donations_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s", report_path.name)
    return 0


def _run_social_x(args: argparse.Namespace) -> int:
    db = Path(args.db)
    create_schema(db)
    con = connect(db, write=True)
    try:
        report = x_posts.run(
            con, scope=args.scope, limit=args.limit,
            handles=args.handles.split(",") if args.handles else None,
            min_weight=args.min_weight, max_items=args.max_items, since=args.since,
            refresh=args.refresh, batch_size=args.batch_size, workers=args.workers,
        )
    finally:
        con.close()
    report_path = db.with_name("social_x_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s", report_path.name)
    return 0


def _run_social_review(args: argparse.Namespace) -> int:
    db = Path(args.db)
    create_schema(db)
    con = connect(db, write=True)
    try:
        report = social_review.run(
            con, model=args.model, limit=args.limit, refresh=args.refresh,
            only_matched=not args.all_posts,
            handles=args.handles.split(",") if args.handles else None,
            workers=args.workers,
        )
    finally:
        con.close()
    report_path = db.with_name("social_review_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s", report_path.name)
    return 0


def _run_ai_review(args: argparse.Namespace) -> int:
    db = Path(args.db)
    create_schema(db)
    con = connect(db, write=True)
    try:
        rules = tuple(args.rule.split(",")) if args.rule else ai_review.REVIEWABLE_RULES
        report = ai_review.run(
            con, model=args.model, limit=args.limit, rules=rules, refresh=args.refresh,
            order=args.order, min_amount_cents=round(args.min_amount_brl * 100),
        )
    finally:
        con.close()
    report_path = db.with_name("ai_review_report.json")
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    log.info("wrote %s", report_path.name)
    return 0


def _manifest(args: argparse.Namespace) -> int:
    con = connect(args.db)
    try:
        write_manifest(con, args.out)
    finally:
        con.close()
    log.info("wrote %s", args.out)
    return 0


def _verify(args: argparse.Namespace) -> int:
    con = connect(args.db)
    try:
        results = verify(con, include_api=args.include_api, api_delay_seconds=args.api_delay)
    finally:
        con.close()
    changed = [r for r in results if r["status"] == "changed"]
    errors = [r for r in results if r["status"] == "error"]
    for r in changed:
        print(f"CHANGED: {r['url']}\n  expected {r['expected']}\n  got      {r['got']}",
              file=sys.stderr)
    for r in errors:
        print(f"ERROR (not verified, retry later): {r['url']}\n  {r['error']}", file=sys.stderr)
    log.info("verified %d collections: %d ok, %d changed, %d download errors%s",
             len(results), len(results) - len(changed) - len(errors), len(changed), len(errors),
             "" if args.include_api else " (per-item API lookups skipped; use --include-api)")
    if changed or errors:
        return 1
    log.info("all source files still match the manifest — the build is reproducible")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="elosys")
    p.add_argument("--version", action="version", version=f"elosys {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init-db", help="create the database and apply the schema")
    pi.add_argument("--db", default="elosys.db")
    pi.set_defaults(func=_init_db)

    for cmd, mod, name, helptext in (
        ("tse-candidates", candidates, "tse_candidates", "ingest TSE consulta_cand -> politician_history"),
        ("tse-accounts", accounts, "tse_accounts", "ingest TSE prestação de contas -> campaign_org"),
        ("tse-social", social, "tse_social", "ingest TSE rede_social_candidato -> social_media"),
        ("tse-assets", assets, "tse_assets", "ingest TSE bem_candidato -> declared_assets"),
    ):
        sp = sub.add_parser(cmd, help=helptext)
        sp.add_argument("--db", default="elosys.db")
        sp.add_argument("--years", help="e.g. 2018,2020,2022,2024,2026 (default: all supported)")
        sp.add_argument("--tmp", default=DEFAULT_TMP, help="temporary download directory")
        sp.set_defaults(func=lambda a, _m=mod, _n=name: _run_crawler(a, _m, _n))

    pc = sub.add_parser("receita-cnpj",
                        help="incremental CNPJ registry lookup (BrasilAPI) -> company_registry/company_partner")
    pc.add_argument("--db", default="elosys.db")
    pc.add_argument("--limit", type=int, default=receita_cnpj.DEFAULT_LIMIT,
                    help="how many missing companies to fetch this run (default: %(default)s)")
    pc.add_argument("--order", choices=("money", "id"), default=receita_cnpj.DEFAULT_ORDER,
                    help="'money' = biggest supplier/donor first (~50s ranking scan); 'id' = insertion order "
                         "(default: %(default)s)")
    pc.add_argument("--include-campaign", action="store_true",
                    help="also enrich campaign-committee CNPJs (natureza 409-4), skipped by default")
    pc.add_argument("--cnpjs", help="comma-separated CNPJs to fetch instead of the queue")
    pc.add_argument("--tmp", default=DEFAULT_TMP, help="temporary download directory")
    pc.set_defaults(func=_run_receita_cnpj)

    pf = sub.add_parser("tse-photo-urls",
                        help="incremental DivulgaCandContas fotoUrl lookup -> candidate_photo")
    pf.add_argument("--db", default="elosys.db")
    pf.add_argument("--limit", type=int, default=photo_urls.DEFAULT_LIMIT,
                    help="how many people (missing a lookup) to check this run (default: %(default)s)")
    pf.add_argument("--person-ids", help="comma-separated person ids to fetch instead of the queue")
    pf.add_argument("--years", help="comma-separated years to scope the queue to (e.g. 2026)")
    pf.add_argument("--workers", type=int, default=photo_urls.DEFAULT_WORKERS,
                    help="concurrent requests (I/O-bound thread pool). Higher = faster but risks the "
                         "source's bot filter blocking the IP -- raise carefully (default: %(default)s)")
    pf.add_argument("--tmp", default=DEFAULT_TMP, help="temporary download directory")
    pf.set_defaults(func=_run_photo_urls)

    ps = sub.add_parser("transparencia-sanctions",
                        help="ingest CEIS/CNEP (Portal da Transparencia) -> sanction")
    ps.add_argument("--db", default="elosys.db")
    ps.add_argument("--tmp", default=DEFAULT_TMP, help="temporary download directory")
    ps.set_defaults(func=_run_sanctions)

    pe = sub.add_parser("transparencia-earmarks",
                        help="ingest Emendas Parlamentares (Portal da Transparencia) -> "
                             "parliamentary_earmark(_beneficiary)")
    pe.add_argument("--db", default="elosys.db")
    pe.add_argument("--tmp", default=DEFAULT_TMP, help="temporary download directory")
    pe.set_defaults(func=_run_earmarks)

    for cmd, mod, name, helptext in (
        ("rule-disproportionate-expense", disproportionate_expense, "rule_disproportionate_expense",
         "flag campaign_expense rows: cheap-sounding item, disproportionate value"),
    ):
        sp = sub.add_parser(cmd, help=helptext)
        sp.add_argument("--db", default="elosys.db")
        sp.set_defaults(func=lambda a, _m=mod, _n=name: _run_rule(a, _m, _n))

    prc = sub.add_parser("rule-circular-donations",
                         help="find loops of donations/expenses across the whole database (Tarjan SCC + bounded DFS)")
    prc.add_argument("--db", default="elosys.db")
    prc.add_argument("--max-depth", type=int, default=circular_donations.DEFAULT_MAX_DEPTH,
                     help="max cycle length in hops (default: %(default)s)")
    prc.add_argument("--max-fanout", type=int, default=circular_donations.DEFAULT_MAX_FANOUT,
                     help="skip branching through nodes with more edges than this (default: %(default)s)")
    prc.add_argument("--min-amount-brl", type=float,
                     default=circular_donations.DEFAULT_MIN_AMOUNT_CENTS / 100,
                     help="skip a cycle whose total movement is below this many reais (default: %(default)s)")
    prc.set_defaults(func=_run_rule_circular_donations)

    pcsp = sub.add_parser(
        "candidate-supplier-partner",
        help="candidatos sócios de empresas que receberam pagamento de campanha (match não determinístico)")
    pcsp.add_argument("--db", default="elosys.db")
    pcsp.set_defaults(func=lambda a: _run_rule(a, candidate_supplier_partner, "candidate_supplier_partner"))

    par = sub.add_parser("ai-review",
                         help="LLM (DeepSeek) second opinion on signals: rotineiro vs. bizarro. Needs DEEPSEEK_API_KEY")
    par.add_argument("--db", default="elosys.db")
    par.add_argument("--limit", type=int, default=ai_review.DEFAULT_LIMIT,
                     help="how many signals PER RULE to review this run, biggest-money first (default: %(default)s)")
    par.add_argument("--rule", help="comma-separated subset of: circular_donations,disproportionate_expense")
    par.add_argument("--model", default=ai_review.DEFAULT_MODEL, help="DeepSeek model (default: %(default)s)")
    par.add_argument("--order", choices=("amount", "tight"), default="amount",
                     help="'amount' = biggest money first; 'tight' = shortest cycles first (default: %(default)s)")
    par.add_argument("--min-amount-brl", type=float, default=0,
                     help="skip signals moving less than this many reais (default: 0)")
    par.add_argument("--refresh", action="store_true", help="re-review signals already reviewed by this model")
    par.set_defaults(func=_run_ai_review)

    psx = sub.add_parser("social-x",
                         help="coleta posts/replies do X de contas declaradas ao TSE (Apify). Needs APIFY_TOKEN")
    psx.add_argument("--db", default="elosys.db")
    psx.add_argument("--scope", choices=("federal", "deputados", "electeds", "all"), default="federal",
                     help="quais candidatos (default: %(default)s = eleitos dep. federal/senador)")
    psx.add_argument("--limit", type=int, help="máximo de contas a coletar nesta execução")
    psx.add_argument("--handles", help="lista de handles separada por vírgula (ignora --scope)")
    psx.add_argument("--min-weight", choices=("baixa", "media", "alta"), default=x_posts.DEFAULT_MIN_WEIGHT,
                     help="peso mínimo dos termos do léxico (default: %(default)s = todos, recall máx.)")
    psx.add_argument("--max-items", type=int, default=x_posts.DEFAULT_MAX_ITEMS,
                     help="teto de tweets por conta (default: %(default)s)")
    psx.add_argument("--since", default=x_posts.DEFAULT_SINCE, help="data mínima YYYY-MM-DD (default: %(default)s)")
    psx.add_argument("--batch-size", type=int, default=x_posts.DEFAULT_BATCH_SIZE,
                     help="contas por chamada do ator Apify (default: %(default)s)")
    psx.add_argument("--workers", type=int, default=x_posts.DEFAULT_WORKERS,
                     help="chamadas do ator em paralelo (default: %(default)s)")
    psx.add_argument("--refresh", action="store_true", help="re-coleta contas já visitadas")
    psx.set_defaults(func=_run_social_x)

    psr = sub.add_parser("social-review",
                         help="LLM (DeepSeek) classifica posts do X coletados: discurso pejorativo vs. uso legítimo")
    psr.add_argument("--db", default="elosys.db")
    psr.add_argument("--limit", type=int, default=social_review.DEFAULT_LIMIT,
                     help="quantos posts revisar nesta execução (default: %(default)s)")
    psr.add_argument("--model", default=social_review.DEFAULT_MODEL, help="modelo DeepSeek")
    psr.add_argument("--workers", type=int, default=social_review.DEFAULT_WORKERS,
                     help="chamadas DeepSeek em paralelo (default: %(default)s)")
    psr.add_argument("--all-posts", action="store_true",
                     help="revisa também posts que não casaram nenhum termo do léxico")
    psr.add_argument("--handles", help="restringe a estes handles (separados por vírgula)")
    psr.add_argument("--refresh", action="store_true", help="re-revisa posts já revisados por este modelo")
    psr.set_defaults(func=_run_social_review)

    pm = sub.add_parser("manifest", help="write the input manifest (sources + hashes)")
    pm.add_argument("--db", default="elosys.db")
    pm.add_argument("--out", default="manifest.json")
    pm.set_defaults(func=_manifest)

    pv = sub.add_parser("verify", help="re-download sources and check hashes against the build")
    pv.add_argument("--db", default="elosys.db")
    pv.add_argument("--include-api", action="store_true",
                    help="also re-query per-item API lookups (BrasilAPI CNPJ, fotoUrl); slow, rate-limited")
    pv.add_argument("--api-delay", type=float, default=1.0,
                    help="seconds between API re-queries with --include-api (default: 1.0)")
    pv.set_defaults(func=_verify)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
