"""Fetch feeds, keep recent items, dedupe, skip/penalise repeats, enrich top candidates.

Pipeline (each step is a plain function so tests can exercise it offline):

    load_sources -> fetch_all -> filter_recent -> prefilter -> dedupe
                 -> apply_history -> (rank) -> enrich_fulltext
"""
from __future__ import annotations

import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit

import feedparser
import requests
import yaml

from . import config, rules
from .textutil import canonical_url, item_id, normalize_title, strip_html, article_text

try:  # rapidfuzz is much faster; difflib keeps things working without it
    from rapidfuzz import fuzz as _fuzz

    def similarity(a: str, b: str) -> float:
        return _fuzz.token_sort_ratio(a, b)

    def _subset(a: str, b: str) -> float:
        return _fuzz.token_set_ratio(a, b)
except ImportError:  # pragma: no cover
    from difflib import SequenceMatcher

    def similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, " ".join(sorted(a.split())), " ".join(sorted(b.split()))).ratio() * 100

    def _subset(a: str, b: str) -> float:
        sa, sb = set(a.split()), set(b.split())
        return 100.0 * len(sa & sb) / max(1, min(len(sa), len(sb)))


def same_story(a: str, b: str) -> bool:
    """Near-identical headlines, or one headline containing the other (prefixes, publisher tags)."""
    if similarity(a, b) >= DUPLICATE_THRESHOLD:
        return True
    return min(len(a.split()), len(b.split())) >= 5 and _subset(a, b) >= 95

log = logging.getLogger(__name__)

GNEWS_URL = "https://news.google.com/rss/search?q={query}+when:{window}&hl={lang}&gl={country}&ceid={country}:{lang}"
DUPLICATE_THRESHOLD = 88      # same story, same day
SEEN_THRESHOLD = 90           # already shown on an earlier day -> skip
SIMILAR_THRESHOLD = 75        # same story by another outlet on an earlier day -> penalise


@dataclass
class Item:
    id: str
    title: str
    url: str
    publisher: str
    source: str
    source_type: str
    lang: str
    region_hint: str
    published: str | None
    snippet: str = ""
    fulltext: str = ""
    also_in: list[str] = field(default_factory=list)
    repeat_of: str | None = None
    penalty: float = 0.0
    prior: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SourceResult:
    name: str
    type: str
    ok: bool
    count: int = 0
    error: str | None = None
    seconds: float = 0.0
    items: list[Item] = field(default_factory=list)


# ----------------------------------------------------------------------------- sources
def load_sources(path: Path | None = None, include_disabled: bool = False) -> list[dict]:
    path = path or config.SOURCES_FILE
    with open(path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    defaults = doc.get("gnews_defaults", {})
    out = []
    for src in doc.get("sources", []):
        if not include_disabled and src.get("enabled", True) is False:
            continue
        src = {**src}
        url = src.get("url")
        if url and not urlsplit(url).scheme and not Path(url).is_absolute():
            src["url"] = str((path.parent / url).resolve())  # local fixture file
        if src["type"] == "gnews":
            src.setdefault("window", defaults.get("window", "2d"))
            src.setdefault("country", "US")
        out.append(src)
    return out


def source_url(src: dict) -> str:
    if src["type"] == "gnews" and not src.get("url"):
        return GNEWS_URL.format(
            query=quote(src["query"]), window=src["window"], lang=src["lang"], country=src["country"].upper()
        )
    return src["url"]


# ----------------------------------------------------------------------------- fetching
def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": config.USER_AGENT, "Accept-Language": "en,az;q=0.9,ru;q=0.8,tr;q=0.7"})
    return s


def _read(url: str, session: requests.Session) -> bytes:
    if url.startswith("file://") or not urlsplit(url).scheme:
        return Path(url.removeprefix("file://")).read_bytes()
    for attempt in range(2):  # one retry for dropped connections
        try:
            resp = session.get(url, timeout=config.HTTP_TIMEOUT)
            break
        except (requests.ConnectionError, requests.Timeout):
            if attempt:
                raise
            time.sleep(2)
    resp.raise_for_status()
    return resp.content


def _parse_date(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        value = entry.get(key)
        if value:
            try:
                return datetime(*value[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                continue
    return None


_BOILERPLATE = re.compile(r"(The post .{0,300}? appeared first on .{0,80}?\.?$)|(\[(…|\.\.\.)\]\s*$)|(Continue reading.*$)", re.I)


def entry_to_item(entry, src: dict) -> Item | None:
    title = strip_html(entry.get("title", ""))
    link = entry.get("link", "")
    if not title or not link:
        return None
    publisher = src["name"]
    if src["type"] == "gnews":
        source_info = entry.get("source") or {}
        publisher = source_info.get("title") or publisher
        suffix = f" - {publisher}"
        if title.endswith(suffix):
            title = title[: -len(suffix)].strip()
    snippet = strip_html(entry.get("summary", "") or entry.get("description", ""))
    snippet = _BOILERPLATE.sub("", snippet).strip()
    # Google News "summaries" just repeat the headline and publisher.
    if src["type"] == "gnews" or normalize_title(snippet).startswith(normalize_title(title)[:40]):
        snippet = ""
    published = _parse_date(entry)
    return Item(
        id=item_id(link, title),
        title=title,
        url=link,
        publisher=publisher,
        source=src["name"],
        source_type=src["type"],
        lang=src.get("lang", "en"),
        region_hint=src.get("region_hint", "global"),
        published=published.isoformat() if published else None,
        snippet=snippet[:1200],
    )


def fetch_source(src: dict, session: requests.Session | None = None) -> SourceResult:
    started = time.monotonic()
    result = SourceResult(name=src["name"], type=src["type"], ok=False)
    if src["type"] == "page":
        result.error = "page sources need the Firecrawl fetcher (not enabled yet)"
        return result
    session = session or _session()
    try:
        raw = _read(source_url(src), session)
        feed = feedparser.parse(raw)
        if feed.bozo and not feed.entries:
            raise ValueError(f"not a feed ({type(feed.bozo_exception).__name__})")
        items = [i for i in (entry_to_item(e, src) for e in feed.entries) if i]
        if src.get("require_keywords"):
            items = [i for i in items if rules.is_fintech(f"{i.title} {i.snippet}")]
        result.items, result.count, result.ok = items, len(items), True
    except Exception as exc:  # network errors, HTTP errors, parse errors
        result.error = f"{type(exc).__name__}: {exc}"[:200]
    result.seconds = round(time.monotonic() - started, 2)
    return result


def fetch_all(sources: list[dict], workers: int = 8) -> list[SourceResult]:
    session = _session()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda s: fetch_source(s, session), sources))


# ----------------------------------------------------------------------------- filters
def filter_recent(items: list[Item], now: datetime, hours: int = config.WINDOW_HOURS) -> list[Item]:
    """Keep items from the last `hours`. Undated items are kept (history check handles repeats)."""
    cutoff = now - timedelta(hours=hours)
    out = []
    for item in items:
        if item.published is None:
            out.append(item)
            continue
        published = datetime.fromisoformat(item.published)
        if cutoff <= published <= now + timedelta(hours=2):
            out.append(item)
    return out


def prefilter(items: list[Item]) -> tuple[list[Item], list[dict]]:
    """Drop items whose headline is clearly on the drop list. Returns (kept, dropped)."""
    kept, dropped = [], []
    for item in items:
        reason = rules.drop_reason(item.title)
        if reason:
            dropped.append({"title": item.title, "url": item.url, "publisher": item.publisher,
                            "reason": f"pre-filter: {reason}"})
        else:
            kept.append(item)
    return kept, dropped


_SOURCE_PREFERENCE = {"rss": 0, "page": 1, "gnews": 2}
_REGION_PREFERENCE = {"azerbaijan": 0, "nearby": 1, "global": 2}


def dedupe(items: list[Item]) -> list[Item]:
    """Merge items with the same canonical URL or a near-identical headline.

    The representative is the one with the most text (RSS over Google News), and
    the other publishers are listed in `also_in`.
    """
    def rank(i: Item):
        return (_SOURCE_PREFERENCE.get(i.source_type, 3), -len(i.snippet), _REGION_PREFERENCE.get(i.region_hint, 3))

    ordered = sorted(items, key=rank)
    kept: list[Item] = []
    seen_urls: dict[str, Item] = {}
    norm_titles: list[tuple[str, Item]] = []
    for item in ordered:
        cu = canonical_url(item.url)
        nt = normalize_title(item.title)
        match = seen_urls.get(cu)
        if match is None and len(nt.split()) >= 4:
            for other_title, other in norm_titles:
                if same_story(nt, other_title):
                    match = other
                    break
        if match is not None:
            if item.publisher != match.publisher and item.publisher not in match.also_in:
                match.also_in.append(item.publisher)
            # a local source hint wins: the story is relevant locally
            if _REGION_PREFERENCE.get(item.region_hint, 3) < _REGION_PREFERENCE.get(match.region_hint, 3):
                match.region_hint = item.region_hint
            continue
        seen_urls[cu] = item
        norm_titles.append((nt, item))
        kept.append(item)
    return kept


# ----------------------------------------------------------------------------- history
def load_history(data_dir: Path, before: str, days: int = config.HISTORY_DAYS) -> list[dict]:
    """Items shown on the `days` days before `before` (YYYY-MM-DD)."""
    shown = []
    cutoff = (datetime.fromisoformat(before) - timedelta(days=days)).date().isoformat()
    for path in sorted(data_dir.glob("????-??-??.json")):
        day = path.stem
        if not (cutoff <= day < before):
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for it in doc.get("items", []):
            shown.append({"date": day, "url": it.get("url", ""), "title": it.get("title", "")})
    return shown


def apply_history(items: list[Item], history: list[dict]) -> tuple[list[Item], list[dict]]:
    """Skip items already shown on an earlier day; penalise the same story from another outlet."""
    if not history:
        return items, []
    seen_urls = {canonical_url(h["url"]): h["date"] for h in history}
    seen_titles = [(normalize_title(h["title"]), h["date"]) for h in history]
    kept, skipped = [], []
    for item in items:
        if canonical_url(item.url) in seen_urls:
            skipped.append({"title": item.title, "url": item.url, "publisher": item.publisher,
                            "reason": f"already shown on {seen_urls[canonical_url(item.url)]}"})
            continue
        nt = normalize_title(item.title)
        best, best_date = 0.0, None
        for title, day in seen_titles:
            s = similarity(nt, title)
            if s > best:
                best, best_date = s, day
        if best >= SEEN_THRESHOLD:
            skipped.append({"title": item.title, "url": item.url, "publisher": item.publisher,
                            "reason": f"already shown on {best_date}"})
            continue
        if best >= SIMILAR_THRESHOLD:
            item.repeat_of = best_date
            item.penalty = config.REPEAT_PENALTY
        kept.append(item)
    return kept, skipped


# ----------------------------------------------------------------------------- candidates
def select_candidates(ranked: list[Item], limit: int, local_reserved: int) -> list[Item]:
    """Top `limit` items by prior, but keep up to `local_reserved` slots for items from
    Azerbaijan sources. Local headlines are often in Azerbaijani or Russian, where the
    keyword prior is weakest, and local finds matter most."""
    local = [i for i in ranked if i.region_hint == "azerbaijan" and rules.is_fintech(i.title)][:local_reserved]
    chosen = {i.id for i in local}
    rest = [i for i in ranked if i.id not in chosen][: max(0, limit - len(local))]
    chosen |= {i.id for i in rest}
    return [i for i in ranked if i.id in chosen]


# ----------------------------------------------------------------------------- full text
def has_direct_link(item: Item) -> bool:
    """Google News RSS links open the article through a browser redirect only, so
    their text cannot be fetched directly. Those items are scored on headline + publisher."""
    return "news.google.com" not in item.url


def fetch_fulltext(item: Item, session: requests.Session | None = None) -> str:
    if not has_direct_link(item):
        return ""
    session = session or _session()
    try:
        resp = session.get(item.url, timeout=12)
        if resp.status_code != 200 or "html" not in resp.headers.get("content-type", ""):
            return ""
        return article_text(resp.text, config.FULLTEXT_CHARS)
    except Exception:
        return ""


def enrich_fulltext(items: list[Item], top_n: int = config.FULLTEXT_TOP_N, workers: int = 8) -> int:
    """Fetch article text for the top `top_n` direct-link items (call after ranking).
    Returns how many succeeded."""
    targets = [i for i in items if has_direct_link(i)][:top_n]
    session = _session()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        texts = list(pool.map(lambda i: fetch_fulltext(i, session), targets))
    ok = 0
    for item, text in zip(targets, texts):
        if text:
            item.fulltext = text
            ok += 1
    return ok
