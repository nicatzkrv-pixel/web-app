"""Fintech Radar CLI.

    python -m radar.main check-sources           per-source item counts + health flags
    python -m radar.main run                     fetch, score, save data/YYYY-MM-DD.json, build site/
    python -m radar.main run --offline           same, from tests/fixtures (no network)
    python -m radar.main build                   rebuild site/ from data/*.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config, fetch, score, simulate, source_health
from .build import build_site

FIXTURE_SOURCES = config.ROOT / "tests" / "fixtures" / "sources.yaml"
BAKU_UTC_OFFSET = 4


def _now(arg: str | None) -> datetime:
    if arg:
        dt = datetime.fromisoformat(arg)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _edition_date(now: datetime) -> str:
    """The bulletin date is the Baku calendar day (UTC+4)."""
    from datetime import timedelta

    return (now + timedelta(hours=BAKU_UTC_OFFSET)).date().isoformat()


def _fixture_now() -> str | None:
    import yaml

    doc = yaml.safe_load(FIXTURE_SOURCES.read_text(encoding="utf-8"))
    return doc.get("fixture_now")


# ----------------------------------------------------------------------------- check-sources
def cmd_check_sources(args) -> int:
    sources = fetch.load_sources(Path(args.sources) if args.sources else None)
    now = _now(args.now)
    print(f"Checking {len(sources)} sources at {now:%Y-%m-%d %H:%M} UTC\n")
    results = fetch.fetch_all(sources)
    width = max(len(s["name"]) for s in sources)
    print(f"{'source'.ljust(width)}  type   status  items  36h   secs")
    print("-" * (width + 38))
    total = recent_total = 0
    for r in results:
        recent = len(fetch.filter_recent(r.items, now)) if r.ok else 0
        total += r.count
        recent_total += recent
        status = "ok" if r.ok else "FAIL"
        line = f"{r.name.ljust(width)}  {r.type:<5}  {status:<6}  {r.count:>5}  {recent:>4}  {r.seconds:>5}"
        if r.error:
            line += f"  {r.error}"
        elif r.ok and r.count == 0:
            line += "  (no items)"
        print(line)
    failed = [r for r in results if not r.ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} sources ok, {total} items, {recent_total} in the last {config.WINDOW_HOURS}h")

    data_dir = Path(args.data_dir) if args.data_dir else config.data_dir()
    if args.record:
        health = source_health.record(data_dir, results, now.isoformat())
    else:
        health = source_health.load(data_dir)
    flagged = source_health.flagged(health, now)
    if flagged:
        print("\nFlagged (failing in more than 50% of runs over 7 days):")
        for name, info in flagged.items():
            print(f"  - {name}: {info['failures']}/{info['runs']} failed. Last error: {info['last_error']}")
    quiet = source_health.quiet(health, now)
    if quiet:
        print("\nQuiet (working but returned nothing on every run this week): " + ", ".join(quiet))
    if args.strict and len(failed) == len(results):
        return 1
    return 0


# ----------------------------------------------------------------------------- run
def cmd_run(args) -> int:
    log = logging.getLogger("radar")
    sources_path = Path(args.sources) if args.sources else None
    now_arg = args.now
    if args.offline:
        sources_path = FIXTURE_SOURCES
        now_arg = now_arg or _fixture_now()
    now = _now(now_arg)
    date = args.date or _edition_date(now)
    data_dir = Path(args.data_dir) if args.data_dir else config.data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    sources = fetch.load_sources(sources_path)
    log.info("Fetching %d sources", len(sources))
    results = fetch.fetch_all(sources)
    if not args.offline:
        source_health.record(data_dir, results, now.isoformat())
    items = [i for r in results for i in r.items]
    stats = {"sources": len(sources), "sources_ok": sum(r.ok for r in results), "fetched": len(items)}

    items = fetch.filter_recent(items, now)
    stats["recent"] = len(items)
    items, dropped = fetch.prefilter(items)
    stats["after_prefilter"] = len(items)
    items = fetch.dedupe(items)
    stats["after_dedupe"] = len(items)
    items, skipped = fetch.apply_history(items, fetch.load_history(data_dir, date))
    stats["after_history"] = len(items)

    # Rank cheaply, then spend full-text fetches and Claude tokens on the top candidates only.
    for item in items:
        item.prior = score.prior_score(item.to_dict())
    items.sort(key=lambda i: i.prior, reverse=True)
    candidates = fetch.select_candidates(items, args.max_candidates, config.LOCAL_RESERVED)
    stats["candidates"] = len(candidates)
    if not args.offline and not args.no_fulltext:
        stats["fulltext"] = fetch.enrich_fulltext(candidates)
        log.info("Full text fetched for %d items", stats["fulltext"])

    scorer = score.make_scorer(force_keywords=args.keywords_only)
    log.info("Scoring %d candidates with %s", len(candidates), "Claude" if scorer else "keyword fallback")
    scored, meta = score.score_items([c.to_dict() for c in candidates], scorer)
    stats["already_have"] = score.check_existing(scored, scorer)
    kept = sorted((s for s in scored if s["keep"]), key=lambda s: (-s["score"], s["region"] != "Azerbaijan"))
    rejected = [{"title": s["title"], "url": s["url"], "publisher": s["publisher"], "score": s["score"],
                 "reason": s["drop_reason"], "scored_by": s["scored_by"]} for s in scored if not s["keep"]]
    if meta["scorer"] == "keyword" and len(kept) > config.KEYWORD_MAX_KEPT:
        over = kept[config.KEYWORD_MAX_KEPT:]
        kept = kept[: config.KEYWORD_MAX_KEPT]
        rejected += [{"title": s["title"], "url": s["url"], "publisher": s["publisher"], "score": s["score"],
                      "reason": "keyword mode: over the daily cap", "scored_by": "keyword"} for s in over]
    stats["kept"] = len(kept)
    stats["simulations"] = simulate.add_briefs(kept, simulate.make_simulator(force_default=args.keywords_only))

    doc = {
        "date": date,
        "generated_at": now.isoformat(timespec="seconds"),
        "scorer": meta["scorer"],
        "sample": bool(args.offline),
        "scoring": meta,
        "stats": stats,
        "items": kept,
        "dropped": rejected + dropped + skipped,
    }
    out = data_dir / f"{date}.json"
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    log.info("Saved %s: %d kept of %d candidates (%s)", out, len(kept), len(candidates), meta["scorer"])
    if meta["fallback_batches"]:
        log.warning("%d batch(es) fell back to keyword scoring: %s", meta["fallback_batches"], meta["errors"][:2])

    if not args.no_build:
        site = build_site(data_dir, Path(args.site_dir) if args.site_dir else config.site_dir())
        log.info("Built site at %s", site)
    print(json.dumps({"date": date, **stats, "scorer": meta["scorer"]}))
    return 0


def cmd_build(args) -> int:
    data_dir = Path(args.data_dir) if args.data_dir else config.data_dir()
    site = build_site(data_dir, Path(args.site_dir) if args.site_dir else config.site_dir())
    print(f"Built site at {site}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="radar", description="Fintech Radar daily bulletin")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--data-dir", help="daily JSON folder (default: data/ or $RADAR_DATA_DIR)")
        p.add_argument("--sources", help="sources YAML (default: config/sources.yaml)")
        p.add_argument("--now", help="pretend the current time is this ISO timestamp")

    p = sub.add_parser("check-sources", help="fetch every source and print item counts")
    common(p)
    p.add_argument("--record", action="store_true", help="save results to source_health.json")
    p.add_argument("--strict", action="store_true", help="exit 1 if every source fails")
    p.set_defaults(func=cmd_check_sources)

    p = sub.add_parser("run", help="fetch, score, save and build")
    common(p)
    p.add_argument("--site-dir")
    p.add_argument("--date", help="edition date YYYY-MM-DD (default: today in Baku)")
    p.add_argument("--offline", action="store_true", help="use tests/fixtures feeds, no network")
    p.add_argument("--keywords-only", action="store_true", help="skip Claude, use the keyword scorer")
    p.add_argument("--no-fulltext", action="store_true", help="do not fetch article text")
    p.add_argument("--no-build", action="store_true")
    p.add_argument("--max-candidates", type=int, default=config.MAX_CANDIDATES)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("build", help="render the static site from data/*.json")
    p.add_argument("--data-dir")
    p.add_argument("--site-dir")
    p.set_defaults(func=cmd_build)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
