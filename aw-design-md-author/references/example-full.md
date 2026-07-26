---
version: alpha
name: Console UI
description: |
  A dark, information-dense developer console. Calm near-black surfaces, a single
  violet accent used sparingly for action, and system fonts for a native-tool feel.
colors:
  primary: "#816DF8"
  primary-hover: "#A395FF"
  primary-soft: "rgba(129,109,248,0.12)"
  bg: "#0C0C1A"
  surface-sunken: "#09091A"
  surface: "#12122B"
  surface-raised: "#16163A"
  text: "#E2E8F0"
  text-muted: "#8896AA"
  text-dim: "#7A8195"
  on-primary: "#0C0C1A"
  border: "rgba(129,109,248,0.10)"
  border-strong: "rgba(129,109,248,0.28)"
  success: "#10B981"
  warning: "#F59E0B"
  danger: "#EF4444"
typography:
  display:
    fontFamily: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: -0.02em
  title:
    fontFamily: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif
    fontSize: 16px
    fontWeight: 700
    lineHeight: 1.25
  body:
    fontFamily: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif
    fontSize: 12px
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: 0.05em
  code:
    fontFamily: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: 8px
  md: 12px
  lg: 16px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 20px
  2xl: 32px
components:
  page:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.text}"
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: 8px 16px
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-ghost:
    backgroundColor: transparent
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: 8px 16px
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: 20px
  card-hover:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.text}"
  input:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: 8px 12px
  metadata:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-muted}"
  metadata-dim:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-dim}"
  divider:
    backgroundColor: "{colors.border}"
  focus-edge:
    backgroundColor: "{colors.border-strong}"
  focus-wash:
    backgroundColor: "{colors.primary-soft}"
  status-success:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.success}"
  status-warning:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.warning}"
  status-danger:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.danger}"
  badge:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.primary}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: 2px 8px
---

<!--
  Illustrative standalone/full-contract example. Use this when DESIGN.md owns
  component appearance or must travel without an authoritative component
  library. Values are invented; the point is the shape: flat frontmatter, the
  canonical sections in order, and prose that says WHEN to use each value.
-->

# Console UI

## Overview

Calm, precise, information-dense — a native developer tool, not a marketing
surface. The interface should feel like a late-night terminal session:
low-light, low-distraction, everything in service of the data. The audience are
engineers who already know the domain, so the console favors density and
scannability over hand-holding. A single accent does the persuading; everything
else stays quiet so that accent reads.

## Colors

Near-black surfaces carry a single violet accent, rationed to well under ~10% of
any screen.

- **Primary `{colors.primary}` (#816DF8):** the only action color — primary
  buttons, active nav, focus rings, links. Never a surface fill or decoration.
- **Surfaces** form a sunken → raised ladder: `{colors.surface-sunken}` for input
  wells (they sit *below* the cards that contain them), `{colors.surface}` for
  cards, `{colors.surface-raised}` for hover and elevated states. Depth reads
  from the ladder, not from heavy fills.
- **Text** is a three-step ladder: `{colors.text}` for headings and body,
  `{colors.text-muted}` for secondary labels, `{colors.text-dim}` for timestamps
  and placeholders. `text-dim` measures ~4.7:1 on `{colors.surface}` — it clears
  WCAG AA-Normal but remains intentionally low-emphasis, so reserve it for
  non-essential metadata.
- **Semantic** `{colors.success}` / `{colors.warning}` / `{colors.danger}` appear
  only in feedback — status, validation, destructive actions — never as
  decoration.

## Typography

System font stacks carry the whole system — no web font is loaded, which is what
makes it read as a native tool. `{typography.code}` (monospace) is reserved for
data that must align: IDs, timestamps, numeric columns.

- **Display / Title** set headings sentence-case; the weight ceiling is 700.
- **Label** is the eyebrow voice — 12px, semibold, UPPERCASE with 0.05em tracking
  — for section headers, form labels, and table headers. Uppercase is never used
  for headings or body copy.

## Layout

A single centered column on an 8px base scale (`{spacing.xs}`–`{spacing.2xl}`).
Whitespace separates *bands*, not the rows inside them: section gaps are generous
(`{spacing.xl}`) while card interiors stay tight (`{spacing.sm}`–`{spacing.md}`).
The result reads dense-but-scannable — large gaps outside, tight rhythm inside.
The content column caps around 1600px, and page padding stays constant across
breakpoints rather than expanding.

## Elevation & Depth

Depth comes from the surface ladder plus a hairline, not from heavy shadows —
near-black eats soft drops.

- **Flat (L0):** the page and full-bleed regions — no border, no shadow.
- **Hairline (L1):** default cards and inputs — 1px `{colors.border}` only. The
  translucent-violet hairline reads because the near-black-to-card luminance step
  already does most of the boundary work.
- **Raised (L2):** hover and dialogs — a single deep drop
  (`0 4px 20px rgba(0,0,0,0.55)`) plus a `{colors.border-strong}` edge.

## Shapes

Each radius signals a category. `{rounded.sm}` for interactive controls (buttons,
inputs, tabs); `{rounded.md}` for cards; `{rounded.full}` for *data* (badges,
chips, status pills). Pills are for data and small radii are for controls, so the
two never share a row.

## Components

- **Button — `{components.button-primary}`:** the violet CTA; one primary action
  per view. Hover swaps to `{components.button-primary-hover}`; disabled drops to
  50% opacity. `{components.button-ghost}` is the transparent secondary for
  toolbars and inline actions.
- **Card — `{components.card}`:** the default surface at L1. An optional UPPERCASE
  `{typography.label}` header strip separates title from body.
- **Input — `{components.input}`:** sits on `{colors.surface-sunken}` so it reads
  as a well; focus raises the border to `{colors.primary}` with a soft
  `{colors.primary-soft}` ring — a halo, never a hard outline. Error state swaps
  the border and helper text to `{colors.danger}`.
- **Badge — `{components.badge}`:** a `{rounded.full}` pill pairing a soft tint
  background with a saturated foreground; for status and counts, not actions.

## Do's and Don'ts

- Do reserve `{colors.primary}` for the single most important action per screen.
- Do set section headers, labels, and table headers in `{typography.label}` —
  UPPERCASE is the hierarchy signal that sections the layout without rules.
- Do use `{typography.code}` with tabular numbers wherever values must align.
- Don't render headings in all-caps — UPPERCASE is the eyebrow voice only.
- Don't use `{colors.text-dim}` for essential text; passing contrast does not make
  the lowest-emphasis rung appropriate for critical information.
- Don't introduce a second accent hue — the palette is closed at one violet plus
  the semantic set. New accents flatten the voice.
- Don't drop a single soft shadow on a card; depth is the surface ladder plus a
  hairline, with one deep drop reserved for L2.
