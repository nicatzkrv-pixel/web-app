"""Render the static site from data/*.json.

    site/index.html                 latest bulletin
    site/archive/YYYY-MM-DD.html    every bulletin, with previous / next navigation
    site/archive/index.html         list of bulletins
    site/data/*.json                the daily data (for the weekly digest and reuse)
    site/assets/                    css, js, fonts
"""
from __future__ import annotations

import json
import re
import shutil
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import config, geo, simulate
from .i18n import t

STATIC_DIR = config.TEMPLATES_DIR / "static"
BAKU = timedelta(hours=4)
REPO_URL = "https://github.com/nicatzkrv-pixel/web-app"


# ----------------------------------------------------------------------------- data
def load_editions(data_dir: Path) -> list[dict]:
    editions = []
    for path in sorted(data_dir.glob("????-??-??.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        doc.setdefault("date", path.stem)
        doc.setdefault("items", [])
        editions.append(doc)
    return editions


def _reason_key(reason: str) -> str:
    if reason.startswith("pre-filter: "):
        return reason.removeprefix("pre-filter: ")
    if reason.startswith("already shown"):
        return "repeat"
    if reason.startswith("score ") or "daily cap" in reason:
        return "below"
    return "judged"


def dropped_summary(doc: dict) -> list[tuple[str, int]]:
    counts = Counter(_reason_key(d.get("reason", "")) for d in doc.get("dropped", []))
    return [(t(f"reason_{k}"), n) for k, n in counts.most_common()]


def score_tiles(score: float) -> list[str]:
    """'9.1' -> ['9', '.', '1']; '10.0' -> ['1','0','.','0']"""
    return list(f"{score:.1f}")


# ----------------------------------------------------------------------------- formatting
def fmt_date_long(day: str) -> str:
    d = datetime.fromisoformat(day)
    return d.strftime("%A %-d %B %Y")


def fmt_date_short(day: str) -> str:
    return datetime.fromisoformat(day).strftime("%-d %b")


def fmt_published(iso: str | None) -> str:
    if not iso:
        return ""
    dt = datetime.fromisoformat(iso) + BAKU
    return dt.strftime("%-d %b, %H:%M")


def fmt_time_baku(iso: str | None) -> str:
    if not iso:
        return ""
    return (datetime.fromisoformat(iso) + BAKU).strftime("%H:%M")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def asset_version() -> str:
    """Short hash of the static files, appended to asset URLs so browsers never mix
    a new page with an old cached stylesheet or script."""
    import hashlib

    h = hashlib.sha1()
    for path in sorted(STATIC_DIR.rglob("*")):
        if path.is_file():
            h.update(path.name.encode())
            h.update(path.read_bytes())
    return h.hexdigest()[:10]


def sim_strings() -> dict:
    from .i18n import STRINGS

    return {k: v for k, v in STRINGS["en"].items() if k.startswith("sim_") or k.startswith("kpi_")}


def _env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals.update(t=t, score_tiles=score_tiles, tojson=lambda v: json.dumps(v, ensure_ascii=False).replace("</", "<\\/"), fmt_published=fmt_published, slug=slug,
                       fmt_date_short=fmt_date_short, categories=config.CATEGORIES, regions=config.REGIONS,
                       repo_url=REPO_URL, min_score=config.MIN_SCORE, v=asset_version(),
                       baseline=simulate.load_baseline(), sim_strings=sim_strings())
    return env


# ----------------------------------------------------------------------------- view model
def edition_view(doc: dict, prev_day: str | None, next_day: str | None, latest_day: str) -> dict:
    items = sorted(doc.get("items", []), key=lambda i: (-i.get("score", 0), i.get("region") != "Azerbaijan"))
    top = items[: config.TOP_PICKS]
    top_ids = {i["id"] for i in top}
    local_all = [i for i in items if i.get("region") == "Azerbaijan"]
    local_rest = [i for i in local_all if i["id"] not in top_ids]
    scored_by = Counter(i.get("scored_by", "keyword") for i in items)
    if items and scored_by.get("claude", 0) == 0:
        scoring_note = "keyword"
    elif scored_by.get("keyword", 0):
        scoring_note = "mixed"
    else:
        scoring_note = None
    present_categories = [c for c in config.CATEGORIES if any(i.get("category") == c for i in items)]
    stats = doc.get("stats", {})

    # Where each item links to on the page, and where it sits on the globe.
    points = []
    for item in items:
        item["anchor"] = f"pick-{item['id']}" if item["id"] in top_ids else f"row-{item['id']}"
        coords = geo.coords_for(item)
        item["place"] = geo.place_name(item) or ""
        if coords:
            points.append({"id": item["id"], "lon": coords[0], "lat": coords[1], "region": item.get("region", "Global"),
                           "score": item.get("score", 0), "idea": item.get("idea", ""),
                           "place": item["place"], "anchor": item["anchor"]})
    sims = {}
    for item in items:
        brief = item.get("sim") or simulate.default_brief(item)
        item["sim"] = brief
        sims[item["id"]] = {**brief, "title": item["title"], "idea": item.get("idea", ""), "url": item["url"],
                            "publisher": item.get("publisher", ""), "category": item.get("category", ""),
                            "region": item.get("region", ""), "place": item.get("place", ""), "kpi": item.get("kpi", "")}
    region_counts = Counter(i.get("region", "Global") for i in items)
    return {
        "date": doc["date"],
        "date_long": fmt_date_long(doc["date"]),
        "day_tiles": datetime.fromisoformat(doc["date"]).strftime("%d"),
        "month_tiles": datetime.fromisoformat(doc["date"]).strftime("%b").upper(),
        "weekday": datetime.fromisoformat(doc["date"]).strftime("%A"),
        "updated": fmt_time_baku(doc.get("generated_at")),
        "all_items": items,
        "top": top,
        "local": local_rest,
        "local_total": len(local_all),
        "local_in_top": len(local_all) - len(local_rest),
        "count": len(items),
        "sources": stats.get("sources_ok") or stats.get("sources"),
        "scoring_note": scoring_note,
        "sample": bool(doc.get("sample")),
        "dropped": dropped_summary(doc),
        "dropped_total": len(doc.get("dropped", [])),
        "present_categories": present_categories,
        "prev_day": prev_day,
        "next_day": next_day,
        "is_latest": doc["date"] == latest_day,
        "points": points,
        "plotted": len(points),
        "region_counts": {r: region_counts.get(r, 0) for r in config.REGIONS},
        "scanned": stats.get("fetched"),
        "ticker": items[:14],
        "sims": sims,
    }


# ----------------------------------------------------------------------------- build
def build_site(data_dir: Path, site_dir: Path) -> Path:
    data_dir, site_dir = Path(data_dir), Path(site_dir)
    editions = load_editions(data_dir)
    env = _env()

    if site_dir.exists():
        shutil.rmtree(site_dir)
    (site_dir / "archive").mkdir(parents=True)
    (site_dir / "data").mkdir()
    shutil.copytree(STATIC_DIR, site_dir / "assets")
    globe = site_dir / "assets" / "radar-globe.js"
    if globe.exists():
        globe.write_text(globe.read_text(encoding="utf-8").replace('"./radar-geo.js"', f'"./radar-geo.js?v={asset_version()}"'), encoding="utf-8")

    edition_tpl = env.get_template("bulletin.html.j2")
    days = [e["date"] for e in editions]
    latest_day = days[-1] if days else None

    for idx, doc in enumerate(editions):
        prev_day = days[idx - 1] if idx > 0 else None
        next_day = days[idx + 1] if idx + 1 < len(days) else None
        view = edition_view(doc, prev_day, next_day, latest_day)
        html = edition_tpl.render(e=view, base="../", page="edition", here=f"archive/{doc['date']}.html")
        (site_dir / "archive" / f"{doc['date']}.html").write_text(html, encoding="utf-8")
        (site_dir / "data" / f"{doc['date']}.json").write_text(
            json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    if editions:
        latest = edition_view(editions[-1], days[-2] if len(days) > 1 else None, None, latest_day)
        index_html = edition_tpl.render(e=latest, base="", page="edition", here="index.html")
        shutil.copyfile(site_dir / "data" / f"{latest_day}.json", site_dir / "data" / "latest.json")
    else:
        index_html = edition_tpl.render(e=None, base="", page="edition", here="index.html")
    (site_dir / "index.html").write_text(index_html, encoding="utf-8")

    rows = []
    for doc in reversed(editions):
        items = sorted(doc.get("items", []), key=lambda i: -i.get("score", 0))
        rows.append({
            "date": doc["date"],
            "date_long": fmt_date_long(doc["date"]),
            "count": len(items),
            "local": sum(1 for i in items if i.get("region") == "Azerbaijan"),
            "top_idea": items[0]["idea"] if items else "",
            "top_score": items[0]["score"] if items else None,
        })
    archive_html = env.get_template("archive.html.j2").render(rows=rows, base="../", page="archive",
                                                              latest_day=latest_day, here="archive/index.html")
    (site_dir / "archive" / "index.html").write_text(archive_html, encoding="utf-8")
    (site_dir / "404.html").write_text(
        env.get_template("404.html.j2").render(base=config.site_base(), page="404", here="404.html"), encoding="utf-8")
    (site_dir / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (site_dir / ".nojekyll").write_text("", encoding="utf-8")
    return site_dir
