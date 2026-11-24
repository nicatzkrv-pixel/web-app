import json
import re

import pytest
from conftest import FIXTURE_SOURCES

from radar import main as cli
from radar.build import build_site, dropped_summary, score_tiles


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """Run the offline pipeline for one day, add an earlier and an empty day, build the site."""
    root = tmp_path_factory.mktemp("radar")
    data, site = root / "data", root / "site"
    assert cli.main(["run", "--offline", "--data-dir", str(data), "--site-dir", str(site), "--no-build"]) == 0
    today = json.loads((data / "2026-03-10.json").read_text())
    earlier = {**today, "date": "2026-03-08", "items": today["items"][:2], "dropped": []}
    empty = {**today, "date": "2026-03-09", "items": [], "dropped": []}
    (data / "2026-03-08.json").write_text(json.dumps(earlier))
    (data / "2026-03-09.json").write_text(json.dumps(empty))
    build_site(data, site)
    return data, site


def read(site, path):
    return (site / path).read_text(encoding="utf-8")


def test_offline_pipeline_output(built):
    data, _ = built
    doc = json.loads((data / "2026-03-10.json").read_text())
    titles = [i["title"] for i in doc["items"]]
    assert doc["sample"] is True and doc["scorer"] == "keyword"
    assert not any("raises $40m" in t or "appoints" in t for t in titles)
    assert sum("QR payments for small merchants" in t for t in titles) == 1
    assert any(i["region"] == "Azerbaijan" for i in doc["items"])
    assert all(i["score"] >= 6 for i in doc["items"])
    assert doc["stats"]["sources_ok"] == 4  # the broken fixture feed is reported, not fatal
    reasons = {d["reason"] for d in doc["dropped"]}
    assert "pre-filter: funding" in reasons and "pre-filter: earnings" in reasons


def test_site_files(built):
    _, site = built
    for path in ["index.html", "archive/index.html", "archive/2026-03-08.html", "archive/2026-03-09.html",
                 "archive/2026-03-10.html", "data/latest.json", "assets/radar.css", "assets/radar.js",
                 "robots.txt", "404.html", ".nojekyll"]:
        assert (site / path).exists(), path
    assert json.loads(read(site, "data/latest.json"))["date"] == "2026-03-10"


def test_index_is_latest_with_sections(built):
    _, site = built
    html = read(site, "index.html")
    assert "Tuesday 10 March 2026" in html
    assert 'name="robots" content="noindex' in html
    for marker in ('id="top-picks"', 'id="local-radar"', 'id="all-items"', "data-filters", "Idea for Birbank"):
        assert marker in html
    assert "Sample data from offline test fixtures" in html
    assert "scored with keyword rules" in html
    assert 'rel="prev"' in html and 'rel="next"' not in html


def test_archive_navigation(built):
    _, site = built
    middle = read(site, "archive/2026-03-09.html")
    assert 'href="../archive/2026-03-08.html" rel="prev"' in middle
    assert 'href="../archive/2026-03-10.html" rel="next"' in middle
    first = read(site, "archive/2026-03-08.html")
    assert 'rel="prev"' not in first
    archive = read(site, "archive/index.html")
    order = re.findall(r'href="(2026-03-\d\d)\.html"', archive)
    assert order == ["2026-03-10", "2026-03-09", "2026-03-08"]


def test_empty_day_shows_empty_states(built):
    _, site = built
    html = read(site, "archive/2026-03-09.html")
    assert "No new items passed the bar today." in html
    assert "No Azerbaijan items today." in html
    assert "data-filters" not in html


def test_empty_site_builds(tmp_path):
    build_site(tmp_path / "nodata", tmp_path / "site")
    assert "No bulletins yet." in read(tmp_path / "site", "index.html")


def test_item_markup_has_score_maths_and_links(built):
    _, site = built
    html = read(site, "index.html")
    assert "How this score adds up" in html
    assert 'target="_blank"' in html and 'rel="noopener"' in html
    assert re.search(r"0\.6 × \d+ \+ 0\.4 × \d+", html)


def test_helpers():
    assert score_tiles(9.1) == ["9", ".", "1"]
    assert score_tiles(10) == ["1", "0", ".", "0"]
    summary = dict(dropped_summary({"dropped": [{"reason": "pre-filter: funding"}, {"reason": "already shown on x"},
                                                 {"reason": "score 5.2 below 6.0"}, {"reason": "funding round"}]}))
    assert summary == {"funding": 1, "already shown": 1, "below the bar": 1, "not a concrete new feature": 1}


def test_fixture_sources_marked_sample():
    assert "SAMPLE DATA" in FIXTURE_SOURCES.read_text()
