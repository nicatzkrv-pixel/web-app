---
version: 1
slug: "templates-bulletin-html-j2"
primary_target: "templates/bulletin.html.j2"
related_targets: []
---

# Surface: daily bulletin (templates/bulletin.html.j2)

Scope: the daily bulletin page, its archive day pages and the archive index. Visitor mode: Read (with light filtering).
Audience and job: Birbank payments management and team, a 2-minute morning scan on phone or laptop; find the idea worth raising today.
Content: real daily items from data/*.json (headline, source, summary, Idea for Birbank, KPI, region, category, launch status, applicability, novelty, score maths).
Constraints: English UI now, all strings in radar/i18n.py for a later Azerbaijani toggle; noindex; no Birbank logo or brand colours; works without JS for reading (filters need JS); 390px and 1280px.

## Direction contract

THESIS: The bulletin is this morning's departures board for ideas: every finding is a row with a status, a destination region and a score, read top to bottom in two minutes. It refuses the news-card grid with thumbnails and the dark SaaS dashboard.

OWN-WORLD: Board teal masthead and section header rows; charcoal split-flap tiles with light digits for scores and the date; a cool paper-white ground with near-black ink; signal amber only for local (Azerbaijan) markers; status colours like a board's: launched green, piloting blue, announced amber-brown. Signage condensed sans (Barlow family) for the board voice and numerals, tabular everywhere; Atkinson Hyperlegible as the reading face. Rows, not cards: hairline row separators inside a board panel.

STORY: The reader sees today's date and how many items and local items there are, reads the top picks' ideas first, checks Local radar, then filters or searches all items if there is time; opens the source for detail; steps back a day through the archive.

FIRST VIEWPORT: Full-width teal masthead: wordmark "Fintech Radar" with "for Birbank", the date in split-flap tiles, counts (items today, local), previous-day and archive links. Directly below, the Top picks board: header row (Score, Idea, Region, Status), then the first pick row at full size: large score tile at left, the Idea for Birbank as the largest text on the page after the wordmark, headline and source beneath, region and category chips, status at right. On 390px the masthead compresses to two lines and the first pick row stacks: tile and status on one line, idea, then headline.

FORM: departures board (timetable tradition), candidate 5 of 7 on my ordered list, seed:0530eae4ac7748b8. Signature interaction: the score tiles flip once on load (top picks only, staggered, reduced-motion respected); the "showing N of M" counter flips when filters change. Motion grammar: one flip, exponential ease-out, nothing else moves.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
