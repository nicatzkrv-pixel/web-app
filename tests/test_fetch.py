import json
from datetime import timedelta

from conftest import FIXTURE_NOW, FIXTURE_SOURCES

from radar import fetch, source_health
from radar.textutil import canonical_url, normalize_title, strip_html


# ----------------------------------------------------------------------------- text helpers
def test_normalize_title_strips_publisher_and_accents():
    assert normalize_title("Leobank launches QR payments - Report.az") == "leobank launches qr payments"
    assert normalize_title("Türkiye: FAST ödeme!") == "turkiye fast odeme"


def test_canonical_url_drops_tracking_and_www():
    a = canonical_url("https://www.example.com/news/item/?utm_source=rss&utm_medium=feed")
    b = canonical_url("http://example.com/news/item")
    assert a == b


def test_strip_html():
    assert strip_html("<p>Hello&nbsp;<b>world</b></p><script>x()</script>") == "Hello world"


# ----------------------------------------------------------------------------- sources + fetching
def test_load_sources_skips_disabled_and_resolves_fixture_paths(fixture_sources):
    names = [s["name"] for s in fixture_sources]
    assert "Disabled Page" not in names
    trade = next(s for s in fixture_sources if s["name"] == "Sample Trade Press")
    assert trade["url"].endswith("tests/fixtures/feeds/trade.xml")


def test_real_sources_file_is_valid():
    sources = fetch.load_sources(include_disabled=True)
    assert len(sources) >= 34
    for s in sources:
        assert s["type"] in ("rss", "gnews", "page"), s
        assert s.get("url") or s.get("query"), s
        assert s["region_hint"] in ("azerbaijan", "nearby", "global"), s
        assert s["lang"] in ("en", "az", "ru", "tr"), s
    langs = {s["lang"] for s in sources}
    assert {"en", "az", "ru", "tr"} <= langs


def test_gnews_url_pattern():
    url = fetch.source_url({"type": "gnews", "query": "Kaspi launch", "window": "2d", "lang": "ru", "country": "KZ"})
    assert url == "https://news.google.com/rss/search?q=Kaspi%20launch+when:2d&hl=ru&gl=KZ&ceid=KZ:ru"


def test_fetch_reports_per_source_status(fetched):
    by_name = {r.name: r for r in fetched}
    assert by_name["Sample Trade Press"].ok and by_name["Sample Trade Press"].count == 7
    assert not by_name["Broken Feed"].ok and by_name["Broken Feed"].error


def test_gnews_entries_use_publisher_and_strip_suffix(all_items):
    item = next(i for i in all_items if "QR payments for small merchants in Baku" in i.title)
    assert item.publisher == "Sample Report"
    assert not item.title.endswith("Sample Report")
    assert item.snippet == ""  # Google News descriptions only repeat the headline


# ----------------------------------------------------------------------------- filters
def test_filter_recent_keeps_36h_and_undated(all_items):
    recent = fetch.filter_recent(all_items, FIXTURE_NOW)
    titles = {i.title for i in recent}
    assert not any(t.startswith("Old item") for t in titles)
    assert any(t.startswith("Undated item") for t in titles)


def test_prefilter_applies_drop_list(all_items):
    kept, dropped = fetch.prefilter(all_items)
    reasons = {d["title"]: d["reason"] for d in dropped}
    assert reasons["Paytech startup Lumen raises $40m Series B to expand in Europe"] == "pre-filter: funding"
    assert reasons["Harbor Bank appoints new chief digital officer"] == "pre-filter: people"
    assert reasons["Payments Summit 2026 announces its speaker line-up"] == "pre-filter: event"
    assert reasons["Sample bank net profit rose in 2025 results"] == "pre-filter: earnings"
    assert "pre-filter: opinion" in reasons.values()
    assert any("tap to pay" in i.title for i in kept)


def test_dedupe_by_url_and_fuzzy_headline(all_items):
    deduped = fetch.dedupe(fetch.filter_recent(all_items, FIXTURE_NOW))
    northwind = [i for i in deduped if "Northwind" in i.title]
    assert len(northwind) == 1, "same URL with tracking params must merge"
    qr = [i for i in deduped if "QR payments for small merchants" in i.title]
    assert len(qr) == 1, "near-identical headlines must merge"
    assert qr[0].also_in == ["Sample Trend"] or qr[0].also_in == ["Sample Report"]


def test_history_skips_shown_and_penalises_similar(all_items, tmp_path):
    items = fetch.dedupe(fetch.filter_recent(all_items, FIXTURE_NOW))
    yesterday = (FIXTURE_NOW - timedelta(days=1)).date().isoformat()
    (tmp_path / f"{yesterday}.json").write_text(json.dumps({"items": [
        {"url": "https://trade.example.com/news/pioneer-softpos", "title": "anything"},
        {"url": "https://other.example.com/x", "title": "Coral Pay starts request-to-pay pilot for utility bills"},
    ]}))
    history = fetch.load_history(tmp_path, FIXTURE_NOW.date().isoformat())
    kept, skipped = fetch.apply_history(items, history)
    assert any("Pioneer" in s["title"] for s in skipped)
    coral = next(i for i in kept if "Coral Pay" in i.title)
    assert coral.penalty > 0 and coral.repeat_of == yesterday


def test_history_ignores_same_day_and_old_files(tmp_path):
    today = FIXTURE_NOW.date().isoformat()
    (tmp_path / f"{today}.json").write_text(json.dumps({"items": [{"url": "u", "title": "t"}]}))
    (tmp_path / "2025-01-01.json").write_text(json.dumps({"items": [{"url": "u2", "title": "t2"}]}))
    assert fetch.load_history(tmp_path, today) == []


def test_fulltext_skips_google_news_links(all_items):
    gn = next(i for i in all_items if i.source_type == "gnews")
    assert not fetch.has_direct_link(gn)
    assert fetch.fetch_fulltext(gn) == ""


# ----------------------------------------------------------------------------- source health
def test_source_health_flags_failing_sources(fetched, tmp_path):
    for day in range(4):
        when = (FIXTURE_NOW - timedelta(days=day)).isoformat()
        source_health.record(tmp_path, fetched, when)
    health = source_health.load(tmp_path)
    flagged = source_health.flagged(health, FIXTURE_NOW)
    assert "Broken Feed" in flagged
    assert "Sample Trade Press" not in flagged
    assert flagged["Broken Feed"]["rate"] == 1.0


def test_fixture_sources_file_exists():
    assert FIXTURE_SOURCES.exists()
