# Fintech Radar

A daily fintech bulletin for **Birbank** (Kapital Bank, Azerbaijan). Every morning at 06:00 Baku time it:

1. scrapes fintech news from trade press and Google News in English, Azerbaijani, Russian and Turkish,
2. uses Claude to keep only **new features, functionalities and approaches**, and scores how useful each is for Birbank,
3. publishes a static, filterable bulletin with an **"Idea for Birbank"** line on every item.

Score = 0.6 × applicability + 0.4 × novelty, +1.5 for Azerbaijan, +1.0 for nearby markets (Caucasus, Central Asia, Türkiye, CIS, Gulf). Items under 6 are dropped.

## How it fits together

```
config/sources.yaml          41 active sources (rss | gnews | page)
radar/fetch.py               fetch, 36-hour window, drop-list pre-filter, dedupe, repeat skip/penalty, full text
radar/score.py               Claude scoring (Haiku by default), keyword fallback
radar/build.py               static site: latest bulletin, archive pages, archive index
radar/source_health.py       flags sources failing in >50% of runs over 7 days
radar/main.py                CLI: run | check-sources | build
templates/                   Jinja templates, CSS, JS, self-hosted fonts
context/birbank-context.md   bank context the scorer reads (fill in the TODOs)
tests/                       unit tests, offline fixtures, Playwright smoke test
.github/workflows/daily.yml  daily build + GitHub Pages deploy
```

Daily data (`YYYY-MM-DD.json` and `source_health.json`) lives on the **`site-data`** branch, not on `main`.

## Run locally

Python 3.11 or newer.

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

```bash
python -m radar.main run --offline              # sample fixtures, no network or API key; builds site/
python -m radar.main check-sources              # live: item counts per source
python -m radar.main run                        # live: fetch, score, save data/YYYY-MM-DD.json, build site/
python -m radar.main run --keywords-only        # live, without Claude
python -m radar.main build                      # rebuild site/ from data/*.json
```

Open the site over HTTP (font preloads fail under `file://`):

```bash
python -m http.server 8000 --directory site
```

Then go to http://localhost:8000.

Useful options for `run`: `--date`, `--now` (pretend time), `--no-fulltext`, `--max-candidates N`, `--data-dir`, `--site-dir`. `-v` prints debug logs.

## Tests

```bash
pytest                                   # unit tests + Playwright smoke test (skips if no browser)
python tests/smoke_site.py site          # smoke test only: the CI deploy gate
```

If Playwright's own browser can't be installed, point it at any Chromium: `export RADAR_CHROMIUM=/path/to/chromium`.

## Secrets

| Secret | Where | Needed for |
|---|---|---|
| `ANTHROPIC_API_KEY` | GitHub → Settings → Secrets and variables → Actions | Claude scoring. Without it the keyword scorer runs and the site shows a notice. |
| `FIRECRAWL_API_KEY` | same | Later: `page` sources (not implemented yet). |

Locally, export `ANTHROPIC_API_KEY` in your shell. Never commit keys; `.env` files are git-ignored.

Optional environment variables: `RADAR_MODEL` (default `claude-haiku-5-5`), `RADAR_MAX_CANDIDATES` (90), `RADAR_LOCAL_RESERVED` (30 candidate slots kept for Azerbaijan sources), `RADAR_FULLTEXT_TOP_N` (30), `RADAR_DATA_DIR`, `RADAR_SITE_DIR`, `RADAR_SITE_BASE` (URL path for the 404 page, default `/web-app/`).

## Deploy (one-time setup)

1. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
2. Add the `ANTHROPIC_API_KEY` secret.
3. Merge this branch into the default branch (scheduled and manual workflows only run from there).
4. **Actions → Daily bulletin → Run workflow** for a manual first run. Check the bulletin, then leave the schedule on (`0 2 * * *` = 06:00 Baku).

The workflow: install → check sources → run pipeline → unit tests → **smoke test (a failure stops the deploy)** → deploy to Pages → commit the day's JSON to `site-data`. Smoke-test screenshots are uploaded as the `smoke-screenshots` artifact.

The site is public on a free plan (agreed). Every page has `noindex` and `robots.txt` disallows crawling.

## Add a source

Edit `config/sources.yaml`:

```yaml
  - name: My Source                 # unique, shown in check-sources and health
    type: rss                       # rss | gnews | page
    url: https://example.com/feed/  # rss/page; gnews uses `query` instead
    lang: en                        # en | az | ru | tr
    region_hint: global             # azerbaijan | nearby | global
    require_keywords: true          # optional: general-news feeds, keep fintech items only
```

For Google News, use `query:` (Google search syntax, `site:` works) and `country:` (ISO-2, for example `AZ`, `KZ`, `TR`). Then run `python -m radar.main check-sources` and confirm the new source returns items. Sites that block feed readers (Cloudflare) can usually be covered with a `gnews` source and `query: site:example.com`.

Sources that fail in more than half their runs over 7 days are flagged at the end of `check-sources`. Fix or remove them.

## How scoring works

- `fetch.py` keeps items from the last 36 hours, drops obvious funding/M&A/people/earnings/event/opinion headlines, merges duplicates (same URL, or near-identical headlines across languages and outlets), skips stories already shown on an earlier day and penalises repeats of a similar story (−1.5).
- Candidates are ranked by a cheap keyword prior; up to 30 slots are reserved for Azerbaijan sources so local news always reaches Claude. Article text is fetched for the top direct links (Google News items are scored on headline and publisher).
- `score.py` sends batches of 8 to Claude with the rules and `context/birbank-context.md` in a cached system prompt, and gets structured JSON back. Article text is passed as untrusted data. The score is computed in code, never by the model.
- If Claude is unavailable, the keyword scorer takes over for that batch; the site says so.

To change the rules, edit `radar/score.py` and `radar/config.py`, and keep `.claude/skills/birbank-fintech-curator/SKILL.md` in sync.

## Simulate for Birbank

Every item has a **Simulate for Birbank** button that opens a 12-month impact report: estimates for each team KPI (MTU, non-cash transactions, net profit, ecosystem growth, NPS, uptime), low / base / high scenarios, editable assumptions, effort, time to launch, dependencies, risks and a first pilot step.

- `radar/simulate.py` writes a brief per kept item: planning assumptions (adoption, activation, extra transactions, fees, acquisition, NPS, uptime) from Claude, or a cautious default per category when Claude is unavailable. The model never produces the figures.
- The browser computes the figures from Birbank's baselines (`config/birbank-baseline.yaml`). **That file is public:** keep it empty or use public, rounded numbers. Each reader can type the real numbers under "Your numbers" in the report; they are stored only in that browser's localStorage.
- Formulas (per scenario): adopters = active users × adoption; new MTU = adopters × activation; extra non-cash transactions = adopters × extra transactions; net profit a year = 12 × adopters × (extra transactions × (revenue − cost per transaction) + new fees); new customers a year = 12 × new customers a month × acquisition uplift.

## Claude Code setup

Skills in `.claude/skills/` load automatically in Claude Code:

| Skill | Use |
|---|---|
| impeccable ([pbakaus/impeccable](https://github.com/pbakaus/impeccable), b49177d, Apache-2.0) | design workflow; `PRODUCT.md` and `DESIGN.md` are its records |
| design-taste-frontend ([Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), 6c0b5c7, MIT) | anti-generic visual direction |
| birbank-fintech-curator | judge a pasted link the way `score.py` does |
| radar-site-testing | Playwright checks on the built site |
| radar-weekly-digest | weekly management email, 3P update, FAQ |

Optional Anthropic plugins from the brief (install with `/plugin` in a terminal session; check current names first): `frontend-design` from `anthropics/claude-plugins-official`; `webapp-testing`, `skill-creator` and `internal-comms` from `anthropics/skills`.

## Still to do (with the team)

- Fill in the `TODO(team)` sections of `context/birbank-context.md`: current Birbank features, competitor feature table, CBA rules, 10–20 labelled examples, pain points, extra local sources.
- Review a few real days of output, then tune sources and the prompt.
- Later: weekly email digest on a schedule, thumbs up/down feedback, Firecrawl `page` sources and competitor change tracking, Azerbaijani UI (strings are in `radar/i18n.py`).
