---
version: alpha
name: Workbench UI
description: A restrained enterprise workspace backed by an implemented component library.
colors:
  primary: "#172033"
  surface: "#FFFFFF"
  surface-subtle: "#F4F6F9"
  on-surface: "#172033"
  on-surface-muted: "#5C6678"
  line: "#DDE3EC"
  error: "#C93445"
typography:
  headline-md:
    fontFamily: Inter, system-ui, sans-serif
    fontSize: 32px
    fontWeight: 600
    lineHeight: 1.2
  body-md:
    fontFamily: Inter, system-ui, sans-serif
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.6
  label-md:
    fontFamily: Inter, system-ui, sans-serif
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1.2
rounded:
  sm: 6px
  md: 10px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
---

<!--
  Illustrative code-backed example. The repository's component library owns
  exact component appearance, states, behavior, and accessibility. This file
  owns shared visual language and component-selection intent; it intentionally
  has no hand-maintained components YAML.
-->

## Overview

Calm, compact, and operational. The interface prioritizes scanability and
clear action hierarchy over decorative expression.

## Colors

Use `primary` for the highest-priority action and strongest interactive signal.
Use the surface ladder to separate page, work area, and inset content. Reserve
semantic colors for feedback and risk, never decoration.

## Typography

Headings identify work context; body text carries operational detail; labels
name controls and compact metadata. Keep labels short and sentence-case.

## Layout

Compose pages on the shared spacing rhythm. Preserve a stable content width for
scan-heavy work and allow data surfaces to use available width when comparison
benefits from it.

## Elevation & Depth

Prefer tonal separation and hairlines. Use elevation only for temporary layers
and the small number of work surfaces that must hold focus.

## Shapes

Use small radii for compact functional containers, medium radii for grouped
surfaces, and full pills for short data or action objects.

## Components

- Use the primary Button variant for the single strongest action in a view;
  choose lower-emphasis variants for supporting actions.
- Use Input for short free-form values, Select for bounded choices, and Text
  Area for multi-line content.
- Use Table when users compare attributes across rows; use List when objects are
  scanned mainly by title, summary, or action.
- Use Dialog for focused interruption; use a page or panel for sustained work.
- Use Badge for status, category, or count, not as decorative filler.

## Do's and Don'ts

- Do compose the authoritative components and their documented variants.
- Do promote a value into shared tokens only when it carries reusable semantics.
- Don't restate component padding, dimensions, or states in prose.
- Don't rebuild an existing system component with local CSS.
