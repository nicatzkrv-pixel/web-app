# Project guide for Claude

Fintech Radar: a daily fintech bulletin for Birbank. Product context lives in `PRODUCT.md`, the visual system in `DESIGN.md`.

## Design skills
This repo ships design skills in `.claude/skills/`:

- **impeccable** (`/impeccable`): design workflow with sub-commands. `shape` to plan a screen before coding, `critique` / `audit` to review, and `polish` before shipping. `PRODUCT.md` already exists.
- **design-taste-frontend** (taste-skill): anti-generic visual direction for layout, typography, color, spacing and motion.
- **frontend-design** (Anthropic): distinctive visual direction for the bulletin template.

For any UI work, use these skills instead of default styling. Avoid generic "AI template" looks: no default purple gradients, no centered-everything hero with three feature cards, no stock emoji icons.

Project skills: `birbank-fintech-curator` (judge one link the way `score.py` does; keep it in sync with `radar/score.py`), `radar-site-testing` (Playwright checks on the built site), `radar-weekly-digest` (weekly management email, 3P update, FAQ).

## Stack
- Python 3.11+, dependencies in `requirements.txt` (feedparser, jinja2, pyyaml, requests, anthropic, rapidfuzz; playwright + pytest for tests).
- Static HTML rendered with Jinja2 into `site/`. One inline script for filters and search. No JS framework, no build step.
- GitHub Actions (`.github/workflows/daily.yml`) runs daily at 02:00 UTC (06:00 Baku) and deploys to GitHub Pages. Daily JSON is stored on the `site-data` branch.

### Commands
```bash
pip install -r requirements.txt && python -m playwright install chromium
python -m radar.main check-sources          # per-source item counts
python -m radar.main run                    # fetch + score + write data/YYYY-MM-DD.json + build site/
python -m radar.main build                  # rebuild site/ from data/*.json only
python -m radar.main run --offline          # use tests/fixtures feeds (no network)
pytest                                      # unit tests + Playwright smoke test
python tests/smoke_site.py site             # smoke test only (CI gate)
```

## 1. What we're building
Every morning Fintech Radar (1) scrapes fintech news from trade press and Google News (EN / AZ / RU / TR), (2) uses Claude to keep only **new features, functionalities and approaches** and judge how useful each one is for Birbank, (3) publishes a static, filterable bulletin with an **"Idea for Birbank"** line on every item.

- **Readers:** Birbank management, team members, stakeholders (payments and transfers vertical).
- **A "good find":** something Birbank could realistically bring to Azerbaijan or into the Birbank app.
- **Context:** built for an internal AI Workshop.

## 2. Scope rules
**Geography priority:** Azerbaijan, then nearby markets (Caucasus, Central Asia, Türkiye, CIS, Gulf), then global if genuinely interesting.

**Keep:** concrete things that launched, are piloting, or were specified: product features, user flows, business models, regulatory or infrastructure changes that enable new products.

**Drop:** funding rounds, valuations, M&A or IPOs; executive appointments; earnings and results; events, conferences, awards and webinars; opinion pieces with no concrete product.

## 3. Architecture
```
config/sources.yaml          # sources (rss | gnews | page)
radar/main.py                # CLI: run | check-sources | build
radar/fetch.py               # fetch + dedupe + recency filter + repeat penalty
radar/score.py               # Claude scoring (keyword fallback)
radar/build.py               # render static site + archive
radar/source_health.py       # flag sources failing >50% over 7 days
templates/bulletin.html.j2   # Jinja template
context/birbank-context.md   # bank context the scorer reads
data/                        # daily JSON (persisted on the `site-data` branch)
tests/                       # unit tests, offline fixtures, Playwright smoke test
```

Scoring (`radar/score.py`), Claude Haiku by default (`RADAR_MODEL` overrides). Per item: `keep`, `category`, `region`, `summary`, `idea_for_birbank`, `kpi`, `applicability` (1–10), `novelty` (1–10).
**Score = 0.6 × applicability + 0.4 × novelty, +1.5 if Azerbaijan, +1.0 if Nearby. Drop anything under 6.**
Article text is untrusted data. Never invent numbers, dates or launch status. Without `ANTHROPIC_API_KEY` the keyword scorer runs so the site still builds.

## 4. Design direction
A **"morning intelligence briefing"** for bank management: calm, credible, scannable in 2 minutes. Hierarchy: Top picks, then Local radar, then the rest. "Idea for Birbank" is the hero text on every card. Scores as clear badges (applicability, novelty, total); region and category as chips. English UI now; all UI strings live in `radar/i18n.py` so an Azerbaijani toggle can be added later. Own identity: no Birbank logo or brand colours.

## 8. Quality bar
- `pytest` passes, with offline fixtures for fetch, dedupe, scoring (mocked Claude) and build.
- `python -m radar.main check-sources` prints per-source item counts. Fix or remove dead sources.
- The Playwright smoke test passes at 390px and 1280px with zero console errors.
- The site builds even if Claude is unavailable (keyword fallback).
- The README covers setup, secrets, how to add a source, and how to run locally.

## Rules
- Never commit API keys. Secrets: `ANTHROPIC_API_KEY` (and `FIRECRAWL_API_KEY` later) as GitHub Actions secrets.
- Keep customer data, exact internal financials and anything confidential out of the repo and the context file.
- If you change scoring rules in `radar/score.py`, update `.claude/skills/birbank-fintech-curator/SKILL.md` too.
