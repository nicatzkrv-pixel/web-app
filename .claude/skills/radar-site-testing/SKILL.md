---
name: radar-site-testing
description: Test the Fintech Radar bulletin site with Python Playwright - filters, search, archive links, mobile (390px) and desktop (1280px) screenshots, console errors - and run or extend the CI smoke test (tests/smoke_site.py). Use after changing the template, CSS, JS or build.py, or when the daily deploy fails at the smoke-test step.
---

# Radar site testing

Adapted from Anthropic's webapp-testing skill (Apache 2.0) for this repo. The site is static HTML that `radar/build.py` renders from `templates/*.j2` into `site/`.

## Setup
```bash
pip install -r requirements.txt
python -m playwright install chromium        # skip if a Chromium is already available
export RADAR_CHROMIUM=/path/to/chromium      # only if Playwright's own browser can't be installed
```
Always headless, sync API, close the browser. Always serve over HTTP (`tests/smoke_site.py` starts its own server): under `file://` the font preloads fail CORS and show up as console errors that never happen on GitHub Pages.

## The fast path
```bash
python -m radar.main run --offline --site-dir site     # fixtures, no network, no API key
python tests/smoke_site.py site --out test-output      # the CI gate
pytest tests/test_smoke.py                             # same, wrapped in pytest
```
`smoke_site.py` exits 1 on any failure, prints PASS/FAIL per check, and writes `test-output/mobile.png` and `test-output/desktop.png` (full page). Open both screenshots and look at them; a passing run can still look wrong.

## What the smoke test checks
At 390×844 and 1280×900:
- zero console errors, page errors, failed requests or HTTP ≥ 400
- `.board--picks`, `.board--local` exist; picks render or `.empty` shows; local rows render or a note/empty state explains why
- every `[data-item]` has `.item__idea` text, `.item__title a[href]`, `.item__where .chip`, `.item__status .status`
- `document.documentElement.scrollWidth <= viewport width`

At 1280 only:
- filters: `[data-count]` equals visible rows on load; region radio (`input[name=region]`), category select, minimum score (`select[name=min]`) each match a DOM count; `[data-reset]` restores everything
- search (`input[name=q]`): a nonsense query shows `[data-empty]`; a real word narrows results
- archive: `archive/index.html` has one row per `archive/YYYY-MM-DD.html`, newest first, matching `data/latest.json`; every row link and every `a[rel=prev|next]` returns 200

## Real selectors (from the templates)
| What | Selector |
|---|---|
| Item row (all sections) | `[data-item]` with `data-region`, `data-category`, `data-score`, `data-search` |
| Sections | `.board--picks`, `.board--local`, `.board--all` |
| Filter form | `[data-filters]`; fields `q`, `region`, `category`, `min` |
| Visible count / empty state | `[data-count]`, `[data-empty]` |
| Score | `.ring` (top picks, aria-label "Score 8.6 out of 10"), `.score-pill.tile` (lists, archive) |
| Globe | `[data-globe]` canvas, tooltip `[data-globe-tip]`, points JSON `#radar-points`, pause `[data-motion-toggle]` |
| Day navigation | `.mast__nav a[rel=prev]`, `a[rel=next]` |

If you change these in the templates, update `tests/smoke_site.py` in the same commit.

## Adding a check
Add it to `check_bulletin`, `check_filters` or `check_archive` in `tests/smoke_site.py` using `run.check(ok, label, detail)`. Read the generated `site/index.html` to find real selectors; never guess. For anything you're unsure renders, do reconnaissance first: load the page, wait for `networkidle`, screenshot, dump `page.content()`, then write the check.

## In CI
`.github/workflows/daily.yml` runs `python tests/smoke_site.py site` after the build and before the Pages deploy. A failing check stops the deploy, so a broken bulletin never reaches management. When it fails, download the `smoke-screenshots` artifact from the run.

## Report back
List each check as pass or fail with the reason, show both screenshots, and propose a fix for every failure.
