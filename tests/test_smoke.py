"""Runs the Playwright smoke test (tests/smoke_site.py) against a site built from fixtures."""
import json

import pytest

from radar import main as cli
from radar.build import build_site

playwright = pytest.importorskip("playwright.sync_api")


def _browser_available() -> bool:
    import os

    try:
        with playwright.sync_playwright() as p:
            exe = os.environ.get("RADAR_CHROMIUM")
            browser = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
            browser.close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _browser_available(), reason="no Chromium for Playwright (set RADAR_CHROMIUM)")
def test_smoke_site(tmp_path):
    import smoke_site

    data, site = tmp_path / "data", tmp_path / "site"
    assert cli.main(["run", "--offline", "--data-dir", str(data), "--site-dir", str(site), "--no-build"]) == 0
    doc = json.loads((data / "2026-03-10.json").read_text())
    (data / "2026-03-09.json").write_text(json.dumps({**doc, "date": "2026-03-09", "items": [], "dropped": []}))
    build_site(data, site)
    assert smoke_site.main([str(site), "--out", str(tmp_path / "shots")]) == 0
    assert (tmp_path / "shots" / "mobile.png").exists()
    assert (tmp_path / "shots" / "desktop.png").exists()
