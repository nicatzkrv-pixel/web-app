"""Playwright smoke test for the built Fintech Radar site. Used as the CI deploy gate.

    python tests/smoke_site.py site                 # checks, screenshots in test-output/
    python tests/smoke_site.py site --out shots/

Checks, at 390x844 and 1280x900:
  - the page loads with zero console errors and no failed requests
  - Top picks, Local radar and All items exist (or show an empty state)
  - every item card has an idea, a source link, a region and a status
  - no horizontal scroll
  - filters change the visible count, a nonsense search shows the empty state, reset restores
  - archive links and previous/next day links resolve, and the newest archive day matches the bulletin

Set RADAR_CHROMIUM to a Chromium binary if Playwright's own browser is not installed.
Exit code 1 if any check fails.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORTS = {"mobile": (390, 844), "desktop": (1280, 900)}


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve(directory: Path):
    handler = functools.partial(_QuietHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/"


def launch(p):
    exe = os.environ.get("RADAR_CHROMIUM")
    return p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()


class Run:
    def __init__(self):
        self.failures: list[str] = []
        self.passed: list[str] = []

    def check(self, ok: bool, label: str, detail: str = ""):
        (self.passed if ok else self.failures).append(label + (f": {detail}" if detail and not ok else ""))


def watch(page, problems: list[str]):
    page.on("console", lambda m: m.type == "error" and problems.append(f"console: {m.text}"))
    page.on("pageerror", lambda e: problems.append(f"page error: {e}"))
    page.on("requestfailed", lambda r: problems.append(f"request failed: {r.url}"))
    page.on("response", lambda r: r.status >= 400 and problems.append(f"HTTP {r.status}: {r.url}"))


def check_bulletin(page, run: Run, name: str):
    for section in (".board--picks", ".board--local"):
        run.check(page.locator(section).count() == 1, f"{name}: {section} present")
    picks = page.locator(".board--picks [data-item]").count()
    picks_empty = page.locator(".board--picks .empty").count()
    run.check(picks > 0 or picks_empty == 1, f"{name}: top picks rendered or empty state shown")
    local_rows = page.locator(".board--local [data-item]").count()
    local_note = page.locator(".board--local .board__note, .board--local .empty").count()
    run.check(local_rows > 0 or local_note > 0, f"{name}: local radar rendered or explained")

    cards = page.locator("[data-item]")
    bad = page.evaluate("""() => [...document.querySelectorAll('[data-item]')].filter(c =>
        !c.querySelector('.item__idea')?.textContent.trim() ||
        !c.querySelector('.item__title a[href]') ||
        !c.querySelector('.item__where .chip') ||
        !c.querySelector('.item__status .status')).length""")
    run.check(bad == 0, f"{name}: every card has idea, source link, region and status", f"{bad} incomplete")
    if picks:
        run.check(page.locator(".board--all").count() == 1, f"{name}: all items present")
    width = page.evaluate("document.documentElement.scrollWidth")
    run.check(width <= page.viewport_size["width"], f"{name}: no horizontal scroll", f"scrollWidth {width}")
    return cards.count()


def check_filters(page, run: Run):
    if page.locator("[data-filters]").count() == 0:
        run.check(True, "filters: none (no items)")
        return
    rows = page.locator("[data-list] [data-item]")
    total = rows.count()
    visible = lambda: page.locator("[data-list] [data-item]:not([hidden])").count()  # noqa: E731
    count_text = lambda: int(page.locator("[data-count]").inner_text())  # noqa: E731
    run.check(count_text() == total == visible(), "filters: count matches rows on load")

    regions = page.evaluate("() => [...new Set([...document.querySelectorAll('[data-list] [data-item]')].map(r => r.dataset.region))]")
    target = "Azerbaijan" if "Azerbaijan" in regions else regions[0]
    page.locator(f"[data-filters] input[name=region][value='{target}']").check(force=True)
    expected = page.evaluate(f"() => document.querySelectorAll('[data-list] [data-item][data-region=\"{target}\"]').length")
    run.check(visible() == expected == count_text(), f"filters: region {target} shows {expected}", f"visible {visible()}")

    page.locator("[data-filters] [data-reset]").click()
    run.check(visible() == total, "filters: reset restores all rows", f"visible {visible()} of {total}")

    cats = page.locator("[data-filters] select[name=category] option").count()
    if cats > 1:
        page.locator("[data-filters] select[name=category]").select_option(index=1)
        chosen = page.locator("[data-filters] select[name=category]").input_value()
        expected = page.evaluate(f"() => document.querySelectorAll('[data-list] [data-item][data-category=\"{chosen}\"]').length")
        run.check(visible() == expected and expected > 0, f"filters: category {chosen} shows {expected}")
        page.locator("[data-filters] [data-reset]").click()

    page.locator("[data-filters] select[name=min]").select_option("9")
    expected = page.evaluate("() => [...document.querySelectorAll('[data-list] [data-item]')].filter(r => parseFloat(r.dataset.score) >= 9).length")
    run.check(visible() == expected, f"filters: minimum score 9 shows {expected}")
    page.locator("[data-filters] [data-reset]").click()

    page.locator("[data-filters] input[name=q]").fill("zzqx-nothing-matches")
    run.check(visible() == 0 and page.locator("[data-empty]").is_visible(), "search: nonsense query shows the empty state")
    page.locator("[data-empty] [data-reset]").click()
    run.check(visible() == total, "search: clear from the empty state restores rows")

    word = page.evaluate("() => document.querySelector('[data-list] [data-item] .item__title a').textContent.trim().split(/\\s+/).find(w => w.length > 4) || ''")
    if word:
        page.locator("[data-filters] input[name=q]").fill(word.lower())
        run.check(0 < visible() <= total, f"search: '{word.lower()}' narrows results", f"visible {visible()}")
        page.locator("[data-filters] [data-reset]").click()


def check_archive(page, base: str, run: Run, site: Path):
    page.goto(base + "archive/index.html")
    links = page.eval_on_selector_all(".days tbody th a", "els => els.map(e => e.getAttribute('href'))")
    days = sorted(p.stem for p in (site / "archive").glob("????-??-??.html"))
    run.check(len(links) == len(days), "archive: one row per bulletin", f"{len(links)} rows, {len(days)} pages")
    if days:
        run.check(links[0] == f"{days[-1]}.html", "archive: newest first")
        latest_doc = json.loads((site / "data" / "latest.json").read_text(encoding="utf-8"))
        run.check(latest_doc["date"] == days[-1], "archive: newest archive day matches the bulletin date")
    for href in links:
        resp = page.request.get(base + "archive/" + href)
        run.check(resp.status == 200, f"archive: {href} resolves", f"HTTP {resp.status}")
    for day in days:
        page.goto(base + f"archive/{day}.html")
        for rel in ("prev", "next"):
            link = page.locator(f".mast__nav a[rel={rel}]")
            if link.count():
                href = link.get_attribute("href")
                target = page.evaluate(f"() => new URL({json.dumps(href)}, location.href).href")
                resp = page.request.get(target)
                run.check(resp.status == 200, f"archive {day}: {rel} link resolves", f"HTTP {resp.status}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site", nargs="?", default="site")
    parser.add_argument("--out", default="test-output")
    args = parser.parse_args(argv)
    site = Path(args.site).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if not (site / "index.html").exists():
        print(f"FAIL: {site}/index.html not found. Build the site first.")
        return 1

    server, base = serve(site)
    run = Run()
    with sync_playwright() as p:
        browser = launch(p)
        for name, (w, h) in VIEWPORTS.items():
            page = browser.new_page(viewport={"width": w, "height": h})
            problems: list[str] = []
            watch(page, problems)
            page.goto(base + "index.html", wait_until="networkidle")
            check_bulletin(page, run, name)
            if name == "desktop":
                check_filters(page, run)
            page.wait_for_timeout(900)  # let the score tiles finish flipping
            page.screenshot(path=str(out / f"{name}.png"), full_page=True)
            if name == "desktop":
                check_archive(page, base, run, site)
            run.check(not problems, f"{name}: no console errors or failed requests", "; ".join(problems[:5]))
            page.close()
        browser.close()
    server.shutdown()

    for line in run.passed:
        print(f"PASS  {line}")
    for line in run.failures:
        print(f"FAIL  {line}")
    print(f"\n{len(run.passed)} passed, {len(run.failures)} failed. Screenshots in {out}/")
    return 1 if run.failures else 0


if __name__ == "__main__":
    sys.exit(main())
