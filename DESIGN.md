---
name: Fintech Radar
description: A live radar at dawn for fintech ideas, judged for Birbank.
colors:
  night-950: "#050c1d"
  night-900: "#081633"
  night-800: "#0e2149"
  night-700: "#173062"
  night-ink: "#eaf1ff"
  night-muted: "#a9b9d6"
  sweep: "#9ff3e6"
  dawn: "#ff9650"
  az: "#ffb23f"
  az-ink: "#8a4f00"
  az-tint: "#fff4de"
  near: "#ff7a5c"
  near-ink: "#b2381c"
  near-tint: "#ffece6"
  glob: "#86cdff"
  glob-ink: "#195a8c"
  glob-tint: "#e6f3ff"
  paper: "#f3f5fa"
  card: "#ffffff"
  text: "#0b1730"
  text-2: "#3a4862"
  text-3: "#56637c"
  line: "#e1e6f0"
  line-2: "#c6cfdf"
  status-launched: "#147a4b"
  status-piloting: "#2756b0"
  status-announced: "#9a5a0c"
  status-specified: "#6a4ba8"
  status-unclear: "#5b6679"
typography:
  hero:
    fontFamily: "Bricolage Grotesque, Segoe UI, system-ui, sans-serif"
    fontSize: "clamp(2.5rem, 6.4vw, 5.6rem)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "-0.04em"
  section-title:
    fontFamily: "Bricolage Grotesque, Segoe UI, system-ui, sans-serif"
    fontSize: "clamp(1.75rem, 3.2vw, 2.4rem)"
    fontWeight: 750
    lineHeight: 1.05
    letterSpacing: "-0.03em"
  idea-lead:
    fontFamily: "Bricolage Grotesque, Segoe UI, system-ui, sans-serif"
    fontSize: "clamp(1.5rem, 2.8vw, 2.15rem)"
    fontWeight: 700
    lineHeight: 1.16
  idea-pick:
    fontFamily: "Bricolage Grotesque, Segoe UI, system-ui, sans-serif"
    fontSize: "1.3rem"
    fontWeight: 700
    lineHeight: 1.28
  idea-row:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 700
    lineHeight: 1.4
  body:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Bricolage Grotesque, Segoe UI, system-ui, sans-serif"
    fontSize: "0.84rem"
    fontWeight: 600
    lineHeight: 1.2
  data:
    fontFamily: "Geist Mono, ui-monospace, monospace"
    fontSize: "0.95rem"
    fontWeight: 600
    lineHeight: 1
rounded:
  pill: "999px"
  score: "9px"
  control: "10px"
  button: "12px"
  card: "16px"
spacing:
  gutter-mobile: "16px"
  gutter: "32px"
  section-gap: "64px"
  card-pad: "22px"
  topbar: "64px"
components:
  button-light:
    backgroundColor: "#ffffff"
    textColor: "{colors.night-950}"
    rounded: "{rounded.button}"
    height: "2.9rem"
    padding: "0 1.2rem"
  button-primary:
    backgroundColor: "{colors.night-900}"
    textColor: "#ffffff"
    rounded: "{rounded.button}"
    height: "2.9rem"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.button}"
  chip-azerbaijan:
    backgroundColor: "{colors.az-tint}"
    textColor: "{colors.az-ink}"
    rounded: "{rounded.pill}"
  chip-nearby:
    backgroundColor: "{colors.near-tint}"
    textColor: "{colors.near-ink}"
    rounded: "{rounded.pill}"
  chip-global:
    backgroundColor: "{colors.glob-tint}"
    textColor: "{colors.glob-ink}"
    rounded: "{rounded.pill}"
  pick-card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.text}"
    rounded: "{rounded.card}"
    padding: "22px"
  score-pill:
    backgroundColor: "{colors.night-900}"
    textColor: "#ffffff"
    typography: "{typography.data}"
    rounded: "{rounded.score}"
---

# Design System: Fintech Radar

## Overview

**Creative North Star: "A live radar at dawn"**

The bulletin is published at 06:00 Baku time, so the frame is the sky at that hour: deep ink-blue over the Caspian with a warm amber glow at the horizon. In it turns a dotted globe with real coastlines, centred on Baku, with a radar sweep circling it and a blip for every item at the country where it happened. Readers see where today's news is before they read what it is. Hover a blip and its idea appears; hover an item and the globe turns to it.

Below the hero, the page switches to a bright, calm reading ground: white cards, generous spacing, the "Idea for Birbank" line as the biggest text in each card. The frame is expressive; the reading area is quiet and fast to scan.

**Key Characteristics:**
- A full-screen pre-dawn hero with the live radar globe and a headline ticker along its bottom edge.
- Colour carries meaning everywhere: saffron = Azerbaijan, coral = nearby markets, ice blue = global (blips, legend, chips, ticker dots, filter pills).
- One orchestrated entrance (words rise, globe settles, blips pop in, numbers roll up), then only slow ambient motion, all pausable.
- White cards with 16px radii and soft two-layer shadows; the lead pick spans the full width.
- Scores as navy rings (picks) or dark pills (lists) in Geist Mono.

## Colors

### Primary
- **Night** (#050c1d → #173062): hero sky, top bar when scrolled, footer, primary buttons, score pills, selected filter pill.
- **Sweep** (#9ff3e6): the radar sweep, the hero date line and the scoring formula in the footer.
- **Dawn** (#ff9650 at low alpha): the horizon glow at the bottom of every hero.

### Region signals
- **Saffron** #ffb23f (ink #8a4f00, tint #fff4de): Azerbaijan. Also text selection and focus rings.
- **Coral** #ff7a5c (ink #b2381c, tint #ffece6): nearby markets.
- **Ice** #86cdff (ink #195a8c, tint #e6f3ff): global.

### Neutral
- **Paper** #f3f5fa page ground; **card** #ffffff; **text** #0b1730 / #3a4862 / #56637c; **lines** #e1e6f0 / #c6cfdf.

### Named Rules
**The Region Colour Rule.** Saffron, coral and ice always mean Azerbaijan, nearby and global. They never decorate anything else, and score rings stay navy so a coral item never reads as a "bad" score.
**The Status Lamp Rule.** Launch status is a lamp plus a word in its status colour; launched lamps pulse gently.

## Typography

**Bricolage Grotesque** (variable) is the display voice: hero, section titles, idea lines in pick cards, labels, chips, buttons. **Atkinson Hyperlegible** is the reading face for headlines, summaries and idea lines in lists; many readers use English as a second language. **Geist Mono** is for measurements only: scores, counts, dates, the formula. Cyrillic headlines fall back to the system sans.

### Hierarchy
- Hero: Bricolage 800, clamp(2.5rem, 6.4vw, 5.6rem), line-height 0.95, tracking −0.04em, max 12ch.
- Section title: Bricolage 750, clamp(1.75rem, 3.2vw, 2.4rem).
- Lead idea: Bricolage 700, clamp(1.5rem, 2.8vw, 2.15rem), max 28ch. Pick idea: 1.3rem.
- Row idea: Atkinson 700, 1.0625rem. Body: Atkinson 400, 1rem/1.6.
- Labels and chips: Bricolage 600, 0.84rem. Data: Geist Mono 600.

### Named Rules
**The Idea Leads Rule.** In every card and row, the idea for Birbank outranks the headline in size and weight.
**The Mono Is Measurement Rule.** Geist Mono only for numbers, dates and the formula; never running text.

## Layout

Centred wrap of 1200px with 16px gutters on phones and 32px from 720px. The hero is a two-column grid from 900px (copy left, globe right, about 620px) and fills the first screen; below 900px the globe sits on top at up to 420px. Content sections are separated by 64px. Top picks: the lead card spans both columns, the next four sit in a two-column grid from 880px. List rows use a four-column grid from 880px (score, body, region, status). The filter bar is sticky under the 64px top bar.

## Elevation & Depth

Two shadow levels on the light ground: shadow-1 (resting cards, filter bar) and shadow-2 (hovered cards). The hero has depth from its sky gradients and the lit globe body, not from shadows. No glows on UI elements; glow belongs to the blips on the globe only.

## Shapes

Pills (999px) for chips, filter pills, nav links and counts; 9px score pills; 10px inputs; 12px buttons and tooltips; 16px cards, boards and tables.

## Components

### Buttons
Light (white on the night hero), primary (night fill on light ground), ghost (outline on the hero), quiet (outline on light ground). All lift 2px on hover and press to scale 0.98; the hero's main button nudges its arrow.

### Chips
Region chips are pills with a coloured dot in the region tint; category and KPI chips are neutral pills.

### Cards / Containers
Pick cards: white, 1px line border, 16px radius, shadow-1, lift 3px with shadow-2 on hover. The lead card carries a faint radial tint of its region colour in the top-right corner. Lists sit in one white board with hairline separators.

### Inputs / Fields
Search with a drawn magnifier, selects and region pills; paper fill, 10px radius, navy focus ring.

### Navigation
Fixed 64px top bar, transparent over the hero and night-filled once scrolled; nav links are pills. The radar mark's sweep turns slowly.

### Live radar globe (signature)
2D canvas: Fibonacci-lattice dots on real coastlines (the Caspian left as water), a lit body, range rings and bezel ticks, a pale-cyan sweep, Baku marked with a pulsing saffron ring, one blip per located item sized by score and coloured by region. Blips pop in on load and flash when the sweep passes. Hover shows a tooltip (place, score, idea); click scrolls to the item and pings it. Hovering an item turns the globe to its blip. A pause button stops the globe, sweep and ticker; reduced motion shows a still frame.

## Do's and Don'ts

### Do:
- **Do** keep the expressive world in the hero, top bar and footer; keep the reading area calm.
- **Do** use region colours only for region meaning.
- **Do** show the score maths for every item.
- **Do** give every looping motion a pause control and a still state under reduced motion.
- **Do** keep all UI strings in `radar/i18n.py`.

### Don't:
- **Don't** add scroll-triggered fade-ins or parallax; the only entrance is the hero's, once.
- **Don't** put glows, gradients or animation inside cards beyond the lead card's corner tint.
- **Don't** plot a blip for an item whose country is unknown; the hero says how many are on the globe.
- **Don't** use eyebrow labels above headings, side stripes on cards, or emoji icons.
- **Don't** use Birbank or Kapital Bank logos or brand colours.
