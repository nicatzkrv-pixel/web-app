"""Shared paths, constants and editorial vocabulary.

Anything that the scorer, the keyword fallback, the site and the curator skill
must agree on lives here, so there is one place to change it.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
SOURCES_FILE = CONFIG_DIR / "sources.yaml"
CONTEXT_FILE = ROOT / "context" / "birbank-context.md"
TEMPLATES_DIR = ROOT / "templates"


def data_dir() -> Path:
    """Where daily JSON lives. CI points this at a checkout of `site-data`."""
    return Path(os.environ.get("RADAR_DATA_DIR", ROOT / "data"))


def site_base() -> str:
    """URL path the site is served from (GitHub Pages project sites live under /<repo>/)."""
    return os.environ.get("RADAR_SITE_BASE", "/web-app/")


def site_dir() -> Path:
    return Path(os.environ.get("RADAR_SITE_DIR", ROOT / "site"))


# --- Fetching -------------------------------------------------------------
WINDOW_HOURS = 36            # keep items published in the last 36 hours
HISTORY_DAYS = 14            # how far back "already shown" is checked
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36 FintechRadar/1.0"
)
HTTP_TIMEOUT = 20
MAX_CANDIDATES = int(os.environ.get("RADAR_MAX_CANDIDATES", "90"))   # sent to the scorer
LOCAL_RESERVED = int(os.environ.get("RADAR_LOCAL_RESERVED", "30"))  # candidate slots kept for local sources
FULLTEXT_TOP_N = int(os.environ.get("RADAR_FULLTEXT_TOP_N", "30"))  # full text fetched
FULLTEXT_CHARS = 2500

# --- Scoring --------------------------------------------------------------
DEFAULT_MODEL = "claude-haiku-5-5"
MIN_SCORE = 6.0
W_APPLICABILITY = 0.6
W_NOVELTY = 0.4
REGION_BONUS = {"Azerbaijan": 1.5, "Nearby": 1.0, "Global": 0.0}
REPEAT_PENALTY = 1.5          # same story already covered on an earlier day
TOP_PICKS = 5
KEYWORD_MAX_KEPT = 25    # keyword fallback is blunt: cap how much it publishes

CATEGORIES = [
    "Payments",
    "Transfers and remittances",
    "Cards",
    "Lending and BNPL",
    "Savings and wealth",
    "Open banking and APIs",
    "Identity and KYC",
    "Security and fraud",
    "AI in banking",
    "Super-app and lifestyle",
    "SME banking",
    "Regulation and infrastructure",
]

REGIONS = ["Azerbaijan", "Nearby", "Global"]

KPIS = [
    "Net profit",
    "NPS",
    "MTU",
    "Non-cash transactions",
    "Ecosystem growth",
    "System uptime",
]

LAUNCH_STATUSES = ["launched", "piloting", "announced", "specified", "unclear"]

# Countries that count as "Nearby" (Caucasus, Central Asia, Türkiye, CIS, Gulf).
NEARBY_COUNTRIES = {
    "Georgia", "Armenia", "Kazakhstan", "Uzbekistan", "Kyrgyzstan", "Tajikistan",
    "Turkmenistan", "Türkiye", "Turkey", "Russia", "Belarus", "Ukraine", "Moldova",
    "United Arab Emirates", "UAE", "Saudi Arabia", "Qatar", "Bahrain", "Kuwait",
    "Oman", "Iran",
}


def compute_score(applicability: int, novelty: int, region: str, penalty: float = 0.0) -> dict:
    """The one scoring formula. Returns the parts so the site can show the maths."""
    a = max(1, min(10, int(applicability)))
    n = max(1, min(10, int(novelty)))
    base = W_APPLICABILITY * a + W_NOVELTY * n
    bonus = REGION_BONUS.get(region, 0.0)
    total = round(base + bonus - penalty, 1)
    return {
        "applicability": a,
        "novelty": n,
        "base": round(base, 1),
        "bonus": bonus,
        "penalty": penalty,
        "score": total,
    }
