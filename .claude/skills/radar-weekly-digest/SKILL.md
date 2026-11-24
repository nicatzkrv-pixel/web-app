---
name: radar-weekly-digest
description: Turn a week of Fintech Radar items into a short weekly email digest for Birbank management, or write a 3P status update (Progress / Plans / Problems) or a stakeholder FAQ about the Radar project.
---

# Radar weekly digest

Based on the newsletter and 3P formats in Anthropic's internal-comms skill, adapted for the Birbank Fintech Radar.

## Inputs
A week of daily JSON files, from any of:
- the published site: `<pages-url>/data/YYYY-MM-DD.json` (and `data/latest.json`)
- the `site-data` branch: `git fetch origin site-data && git show origin/site-data:YYYY-MM-DD.json`
- a local run: `data/YYYY-MM-DD.json`
- or items pasted by the user.

Each file has `date`, `scorer` and `items[]`. Each item has: `title`, `url`, `publisher`, `published`, `category`, `region` (Azerbaijan / Nearby / Global), `country`, `summary`, `idea`, `kpi`, `launch_status`, `applicability`, `novelty`, `score`, `scored_by`. Use those fields; fill nothing the source does not state.

Load the week, drop exact duplicates across days (same `url` or near-identical `title`; keep the highest score), then rank by `score`, local first on ties.

If most items that week have `scored_by: "keyword"`, say so in one line at the top: those ideas are generic and the ranking is rough.

## Weekly digest (default)
Audience: Birbank management and stakeholders reading on a phone, in email or a chat app. They skim.

1. **Subject line:** "Fintech Radar, week of [Monday date]: [the single biggest idea in 6 words or fewer]".
2. **The one to read** (2–3 sentences): the top-scored item and why it matters for Birbank.
3. **Close to home:** up to 3 items from Azerbaijan or nearby markets.
4. **Worth copying:** up to 5 global items, one bullet each: what launched, where, and the Birbank idea in one clause.
5. **Pattern of the week** (1–2 sentences, only if 3 or more items point the same way).
6. **Footer:** link to the Radar site and archive, plus one line on how to suggest a source (open an issue in the repo).

**Rules**
- 10–12 bullets maximum, each 1–2 sentences.
- "We" voice for Birbank ("we could…"), plain language, no hype words.
- Every item links to its original source (`url`).
- Summarise in your own words; quote at most one short phrase (under 125 characters) per source.
- No funding, earnings, appointment or event news.
- Never invent numbers, dates or launch status. If `launch_status` is `announced`, write "announced", not "launched".
- Fewer than 3 strong items (score ≥ 7)? Send a shorter digest rather than padding it.

## 3P update (for workshop organisers or managers)
Three short sections, 3–5 bullets each:
- **Progress:** what shipped since the last update, with numbers from the data (sources live from `stats.sources_ok`, items kept per day, editions published).
- **Plans:** next steps with owners and dates (ask if unknown).
- **Problems:** blockers and the help needed (for example: context file placeholders, sources flagged by `source_health.json`).

## FAQ
Answer the questions stakeholders actually ask, 1–2 sentences each:
- How are items chosen? (trade press and Google News in EN/AZ/RU/TR; Claude keeps only concrete new features; drop list.)
- What does the score mean? (0.6 × applicability + 0.4 × novelty, +1.5 Azerbaijan, +1.0 nearby; under 6 is dropped.)
- When does it refresh? (daily at 06:00 Baku time.)
- How do I suggest a source? (open an issue in the repo, or edit `config/sources.yaml`.)
- Who owns the Radar? (ask the user if not known.)

## Output
Email-ready text: a subject line, then the body with short headers and bullets. Offer an HTML version if it will be pasted into an email client that renders HTML.
