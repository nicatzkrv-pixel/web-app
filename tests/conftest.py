import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIXTURES = ROOT / "tests" / "fixtures"
FIXTURE_SOURCES = FIXTURES / "sources.yaml"
FIXTURE_NOW = datetime.fromisoformat("2026-03-10T02:00:00+00:00")


@pytest.fixture
def fixture_sources():
    from radar import fetch

    return fetch.load_sources(FIXTURE_SOURCES)


@pytest.fixture
def fetched(fixture_sources):
    from radar import fetch

    return fetch.fetch_all(fixture_sources, workers=2)


@pytest.fixture
def all_items(fetched):
    return [i for r in fetched for i in r.items]
