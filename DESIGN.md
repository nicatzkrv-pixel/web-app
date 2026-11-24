---
name: Fintech Radar
description: A morning departures board for fintech ideas, judged for Birbank.
colors:
  board: "#0f3b3d"
  board-2: "#174b4d"
  board-3: "#215d5e"
  board-ink: "#eef5f2"
  board-muted: "#a8c7c1"
  tile: "#1c2426"
  tile-hi: "#2a3335"
  tile-ink: "#f5f3ed"
  ground: "#edf1ef"
  panel: "#ffffff"
  ink: "#132120"
  ink-2: "#3f4f4e"
  ink-3: "#566665"
  rule: "#dbe3e0"
  rule-strong: "#b9c7c3"
  amber: "#f0b21c"
  amber-ink: "#6e4600"
  amber-tint: "#fff3d3"
  teal-tint: "#e0eeeb"
  teal-ink: "#0d4d4d"
  status-launched: "#18744a"
  status-piloting: "#285aa4"
  status-announced: "#8f540c"
  status-specified: "#5f4b98"
  status-unclear: "#5d6968"
typography:
  wordmark:
    fontFamily: "Barlow Semi Condensed, Arial Narrow, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1
  section-title:
    fontFamily: "Barlow Semi Condensed, Arial Narrow, system-ui, sans-serif"
    fontSize: "1.375rem"
    fontWeight: 600
    lineHeight: 1.2
  idea-pick:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "1.375rem"
    fontWeight: 700
    lineHeight: 1.32
  idea-row:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: 1.35
  body:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Barlow Semi Condensed, Arial Narrow, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.2
  numeral:
    fontFamily: "Barlow Semi Condensed, Arial Narrow, system-ui, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 600
    lineHeight: 1
rounded:
  chip: "4px"
  control: "6px"
  board: "8px"
spacing:
  gutter-mobile: "16px"
  gutter: "28px"
  row-x: "20px"
  row-y: "18px"
  section-gap: "24px"
components:
  button-primary:
    backgroundColor: "{colors.board}"
    textColor: "{colors.board-ink}"
    rounded: "{rounded.control}"
    height: "2.75rem"
    padding: "0 16px"
  button-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.board}"
    rounded: "{rounded.control}"
    height: "2.75rem"
  chip-azerbaijan:
    backgroundColor: "{colors.amber}"
    textColor: "{colors.tile}"
    rounded: "{rounded.chip}"
  chip-nearby:
    backgroundColor: "{colors.teal-tint}"
    textColor: "{colors.teal-ink}"
    rounded: "{rounded.chip}"
  board-head:
    backgroundColor: "{colors.board-2}"
    textColor: "{colors.board-ink}"
    typography: "{typography.section-title}"
  score-tile:
    backgroundColor: "{colors.tile}"
    textColor: "{colors.tile-ink}"
    typography: "{typography.numeral}"
---

# Design System: Fintech Radar

## Overview

**Creative North Star: "This morning's departures"**

Fintech Radar is read in about two minutes, at 8 a.m., on a phone or a laptop. The page borrows the one public document everyone already scans that fast: a departures board. Every finding is a row with a score, a destination (region) and a status (launched, piloting, announced). The board owns the frame (masthead, section header rows, score tiles, footer). The rows inside stay quiet and readable, because the content is the product: the "Idea for Birbank" line is the largest text in every row.

The world never takes over the reading column. There are no flip animations on body text, no LED dot fonts and no dark page. The page sits on a cool paper ground in daylight, with the teal board around it.

**Key Characteristics:**
- Deep teal board frame around a cool paper-white reading ground.
- Split-flap tiles for scores and the date only: one flap per character, a hinge line across the middle.
- Rows, not cards: hairline separators inside a board panel.
- Status lamps in board colours: launched green, piloting blue, announced amber-brown.
- Signal amber marks only one thing: Azerbaijan (local).

## Colors

A restrained strategy with a committed frame. The teal board carries the identity across the masthead, section headers and footer; content sits on neutral paper; colour inside rows always means something.

### Primary
- **Board teal** (#0f3b3d): masthead, Top picks header, footer, primary buttons, selected filter segments. Tints board-2 (#174b4d) and board-3 (#215d5e) for other section headers, hover and the masthead divider.

### Secondary
- **Signal amber** (#f0b21c): local (Azerbaijan) chips, the Local count in the masthead, focus rings, text selection. Its tint (#fff3d3) is the local row wash and the notice ground; amber-ink (#6e4600) is notice text.

### Neutral
- **Cool paper** (#edf1ef) page ground; **panel** (#ffffff) board interiors.
- **Ink** (#132120) ideas and headings; **ink-2** (#3f4f4e) headlines and summaries; **ink-3** (#566665) metadata.
- **Rules** (#dbe3e0 hairlines, #b9c7c3 control borders).
- **Tile** (#1c2426 / #2a3335 halves) with tile-ink (#f5f3ed) digits.

### Named Rules
**The One Signal Rule.** Amber means local. Never use it for decoration, emphasis or "new".
**The Status Lamp Rule.** Launch status is always the lamp-plus-word pair in its status colour, never colour alone.

## Typography

Two faces with separate jobs. **Barlow Semi Condensed** is the board's signage voice: wordmark, section titles, labels, metadata, chips, every numeral (tabular figures everywhere). **Atkinson Hyperlegible** is the reading face for ideas, headlines and summaries. Many readers use English as a second language and read on phones, and Atkinson was designed for exactly that legibility. Cyrillic headlines fall back to the system sans.

### Hierarchy
- Wordmark: Barlow 700, 1.5rem.
- Section title: Barlow 600, 1.375rem, on the board header row.
- Idea (top pick): Atkinson 700, 1.375rem desktop and 1.1875rem mobile, max 62ch.
- Idea (row): Atkinson 700, 1.125rem.
- Headline link: Atkinson 400, 1rem, ink-2, max 70ch.
- Summary: Atkinson 400, 0.9375rem, ink-2, max 68ch (two lines in rows, three in mobile picks).
- Metadata, labels, chips: Barlow 500–600, 0.875–0.9375rem.
- Numerals: Barlow 600, tabular.

### Named Rules
**The Idea Leads Rule.** In every row, the idea for Birbank outranks the headline in size and weight.
**The No Caps Rule.** Labels and statuses are sentence case. The board voice comes from the condensed face, not capitals.

## Layout

One centred column, max 1180px, 16px gutters on phones and 28px from 720px. Section boards stack with 24px gaps. From 880px, every row uses the same four-column grid as its header row (Score, Idea for Birbank, Region, Status), with the score column wider in Top picks (6.25rem) than in other rows (4.75rem). Below 880px a row becomes score tile, with region and status stacked at right, then the body.

## Elevation & Depth

Flat. Depth exists only on the score tiles (a 1–2px soft shadow, as if mounted on the board). Panels are separated by hairline borders and the ground, never by shadows.

## Shapes

Small radii: 4px chips and tiles (0.12em on flaps), 6px controls, 8px board panels. Status lamps are 2px-radius squares.

## Components

### Buttons
Primary: board-teal fill, board-ink label in Barlow 600, 2.75rem tall, 6px radius; hover lightens to board-3, press drops 1px. Quiet: transparent with a rule-strong border and board-teal label.

### Chips
Category: white with rule-strong border. KPI ("Moves MTU"): ground fill. Region: amber fill for Azerbaijan, teal-tint for nearby countries, outline for global.

### Cards / Containers
Board panels: white interior, 1px rule border, 8px radius, a teal header row on top. Item rows inside are separated by hairlines. Local rows carry a faint amber-tint wash that fades to white.

### Inputs / Fields
Search and selects: 2.75rem tall, rule-strong border, 6px radius, white fill, Atkinson 1rem. Region filter is a segmented control; the checked segment fills with board teal.

### Navigation
Masthead links in Barlow 600 on the board, 2.5rem tall, hover board-2, current page board-3. Previous and next day carry drawn chevrons.

### Split-flap score tile (signature)
One dark flap per character, split into a lighter top half and darker bottom half, with a 1px hinge line across the middle and a small square decimal point. Sizes: sm 0.95rem (archive), md 1.5rem (rows), lg 2–2.5rem (top picks), xl 2.1–3.25rem (masthead date). Top-pick tiles flip once on load, staggered by row (0.7s, exponential ease-out); the "showing N" counter flips when filters change. Reduced motion disables both.

## Do's and Don'ts

### Do:
- **Do** keep the board world in the frame: masthead, section header rows, tiles, footer.
- **Do** show the score maths for every item (fit, new, bonus, penalty, total).
- **Do** use tabular Barlow numerals for every number.
- **Do** keep all UI strings in `radar/i18n.py` so the Azerbaijani UI can be added.

### Don't:
- **Don't** add flip animations anywhere but score tiles and the result counter.
- **Don't** use amber for anything other than local (Azerbaijan).
- **Don't** set ideas, headlines or summaries in the condensed board face.
- **Don't** add thumbnails, card grids, eyebrow labels above headings, or side stripes on rows.
- **Don't** use Birbank or Kapital Bank logos or brand colours; the product has its own identity.
