# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Python 3.11+ pipeline (feedparser, requests, PyYAML, Jinja2, anthropic SDK) that renders a static HTML site. Built and deployed daily by GitHub Actions to GitHub Pages. No JavaScript framework: one small inline script handles filters and search. Decided in the build brief (`FINTECH_RADAR_BRIEF` sections 3 and 3.5).

## Users

Birbank management, payments and transfers team members, and stakeholders. Birbank is the digital banking brand of Kapital Bank, Azerbaijan's largest retail bank. They open the bulletin each morning and scan it in about two minutes, roughly as often on a phone as on a laptop. Their job: spot a feature, flow or approach that Birbank could realistically bring to Azerbaijan or into the Birbank app, and decide whether to discuss it.

## Product Purpose

Fintech Radar is a daily bulletin. Every morning it scrapes fintech trade press and Google News (EN, AZ, RU, TR), uses Claude to keep only new features, functionalities and approaches, scores how useful each is for Birbank, and publishes a static, filterable page. Every item has an "Idea for Birbank" line. Success: management reads it daily, and good finds turn into roadmap conversations.

## Positioning

It is not a news feed. Each item has been judged against Birbank's own payments KPIs and against what already exists in Azerbaijan, and turned into one concrete "we could…" idea. Funding, earnings, appointments and events are filtered out on purpose.

## Operating Context

- Built for an internal AI Workshop; a demo exists and the final version is due soon.
- Refreshes daily at 06:00 Baku time (02:00 UTC). Each day has an archive page.
- Geography priority: Azerbaijan, then nearby markets (Caucasus, Central Asia, Türkiye, CIS, Gulf), then global.
- Team KPIs: payments vertical net profit, NPS, MTU, non-cash transactions, ecosystem customer growth, system uptime.

## Capabilities and Constraints

- Sections: Top picks, Local radar (Azerbaijan), All items with category, region and minimum-score filters plus text search; daily archive with navigation between days.
- Scores: applicability (1–10), novelty (1–10), total = 0.6 × applicability + 0.4 × novelty + regional bonus (+1.5 Azerbaijan, +1.0 nearby); under 6 is dropped.
- Must build even when Claude is unavailable (keyword fallback scorer; its scores are marked as such).
- Public GitHub Pages site (confirmed acceptable); pages carry `noindex`. Nothing confidential, no customer data, no exact internal financials.
- English UI now; an Azerbaijani toggle is planned, so copy must live in one place and layouts must tolerate longer strings.
- Must work at 390px and 1280px.

## Brand Commitments

- Own identity, named "Fintech Radar". "for Birbank" appears in text only. No Birbank or Kapital Bank logo or brand colours (confirmed).
- Voice: calm, credible, plain. "We could…" for ideas. No hype.

## Evidence on Hand

- Real content comes from the daily pipeline (`data/*.json`). Offline fixtures in `tests/fixtures/` are sample data for tests only and must never be presented as real news.
- Still missing (placeholders in `context/birbank-context.md`): Birbank feature list and roadmap, competitor feature table, CBA rules, labelled example finds.

## Product Principles

1. The idea is the product: "Idea for Birbank" outranks the headline.
2. Local first: Azerbaijan and nearby markets get visible priority.
3. Show the maths: every score can be checked by the reader.
4. Never overstate: "announced" is not "launched"; no invented numbers.
5. Two minutes or less: if it needs scrolling to understand, it is too long.

## Accessibility & Inclusion

WCAG 2.2 AA contrast and keyboard access for filters and search. Readers use English as a second language, so prefer short, plain sentences.
