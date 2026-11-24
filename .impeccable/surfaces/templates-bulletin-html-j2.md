---
version: 1
slug: "templates-bulletin-html-j2"
primary_target: "templates/bulletin.html.j2"
related_targets: []
---

# Surface: daily bulletin (templates/bulletin.html.j2)

Scope: the daily bulletin page, its archive day pages and the archive index. Visitor mode: Read, with an expressive frame the user asked for ("gorgeous, cool, animated").
Audience and job: Birbank payments management and team, a 2-minute morning scan on phone or laptop; find the idea worth raising today.
Content: real daily items from data/*.json (headline, source, summary, Idea for Birbank, KPI, region, country, category, launch status, applicability, novelty, score maths).
Constraints: English UI now, strings in radar/i18n.py; noindex; no Birbank logo or brand colours; readable without JS (filters and the globe need JS); 390px and 1280px; reduced motion respected.
History: replaces the "morning departures" world, which the user rejected as too plain.

## Direction contract

THESIS: The bulletin is a live radar at dawn: today's finds appear as blips on a turning globe centred on Baku, so the reader sees where the news is before reading what it is. Refuses the static news list and the dark neon dashboard.

OWN-WORLD: A pre-dawn sky over the Caspian for the frame: deep ink-blue hero with a faint amber dawn glow at the horizon, a dotted globe with real coastlines, a thin pale-cyan radar sweep. Blip colours carry meaning: saffron for Azerbaijan, coral for nearby markets, ice blue for global. Below the hero, a bright cool-white reading ground with white cards, soft shadows and 14px radii. Bricolage Grotesque for display, Atkinson Hyperlegible for reading, Geist Mono for scores and counts.

STORY: The reader sees today's count and where the finds are on the globe, hovers a blip to read its idea, then reads the top picks, checks Local radar, filters All items if there is time, and steps back a day through the archive.

FIRST VIEWPORT: Desktop: ink-blue hero filling the screen. Left: the h1 "25 finds on today's radar", a line with the date and what was scanned, three region counters that double as the globe's legend, and a primary "Read the top picks" button. Right: the globe, about 560px, Baku marked with a pulsing ring, blips per item, the sweep circling. A headline ticker runs along the hero's bottom edge. Mobile: the globe on top at about 300px, then the h1, counters and button.

FORM: live radar globe (my top-ranked grounded candidate, chosen by the user over the assigned carpet geometry), seed:d13d332e601202a2. Signature interaction: hovering or focusing a blip shows that item's idea and score; clicking it scrolls to the item and highlights it, and hovering an item makes its blip pulse. Motion grammar: one orchestrated entrance (headline words rise, globe settles, blips pop in order, counters and score rings roll up), then only the slow globe turn, the sweep and the ticker, all pausable; hover answers on every card, button and link.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
