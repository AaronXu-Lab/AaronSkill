# DESIGN.md — Spec Summary (condensed from the official Google Labs spec, version: alpha)

Source of truth: https://github.com/google-labs-code/design.md (`docs/spec.md`). This is a working condensation for offline use; when in doubt, run `npx @google/design.md spec`.

## Structure

Two layers:
1. **Optional YAML frontmatter** between `---` fences at the very top → machine-readable tokens (normative when present).
2. **Markdown body** → `##` sections of human-readable rationale.

Prose may use descriptive color names that correspond to systematic token names. Tokens are the normative values; prose provides context.

## Token schema

```yaml
version: <string>          # optional, current: "alpha"
name: <string>
description: <string>      # optional
colors:
  <token-name>: <Color>          # Any valid CSS color; hex is recommended
typography:
  <token-name>: <Typography>
rounded:
  <scale-level>: <Dimension>     # xs|sm|md|lg|xl|full or any string
spacing:
  <scale-level>: <Dimension | number>
components:
  <component-name>:
    <token-name>: <string | {token reference}>
```

Token groups and Markdown sections may be omitted when they are not relevant. `components:` is supported, not required.

### Types

- **Color**: any valid CSS color string, including hex, named colors, `rgb()`/`hsl()`, wide-gamut functions, and `color-mix()`. Hex remains the recommended default. Values are converted to sRGB for contrast checks while the original form is preserved.
- **Dimension**: number + unit; valid units `px`, `em`, `rem` (e.g. `48px`, `-0.02em`).
- **Token reference**: `{path.to.token}` → must resolve to a primitive (e.g. `{colors.primary}`); composite refs (e.g. `{typography.label-md}`) allowed only inside `components`.
- **Typography** object fields: `fontFamily` (string), `fontSize` (Dimension), `fontWeight` (number), `lineHeight` (Dimension or unitless multiplier), `letterSpacing` (Dimension), `fontFeature` (string), `fontVariation` (string).

### Component property tokens

`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`.
Variants (hover/active/pressed) = separate entries with related keys, e.g. `button-primary`, `button-primary-hover`.

## Section order (canonical — present sections must follow this sequence)

| # | Section | Aliases |
|---|---------|---------|
| 1 | Overview | Brand & Style |
| 2 | Colors | |
| 3 | Typography | |
| 4 | Layout | Layout & Spacing |
| 5 | Elevation & Depth | Elevation |
| 6 | Shapes | |
| 7 | Components | |
| 8 | Do's and Don'ts | |

- All sections use `##`. An optional `#` H1 title may precede Section 1 (not parsed as a section).
- **Duplicate `##` section heading → file is rejected.** Unknown sections are preserved, not errored.

### What each section is for

- **Overview** — brand personality, audience, emotional response; foundational context for decisions not covered by an explicit token.
- **Colors** — define palettes; at least `primary` should exist. Convention: `primary`, `secondary`, `tertiary`, `neutral`. Tokens derive from the palettes described in prose.
- **Typography** — usually 9–15 levels; semantic categories (`headline`, `display`, `body`, `label`, `caption`) × sizes (`sm`/`md`/`lg`).
- **Layout** (Layout & Spacing) — grid/margins/safe-areas strategy + a spacing scale.
- **Elevation & Depth** — how hierarchy is conveyed (shadows, or for flat designs: borders/tonal layers/contrast).
- **Shapes** — corner-radius language; the `rounded` scale.
- **Components** — optional per-component sub-token groups, with variants; values may be literals or references. The component schema is actively evolving.
- **Do's and Don'ts** — specific, token-citing guardrails (not generic UX advice).

## Recommended (non-normative) token names

- **Colors**: `primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `error`
- **Typography**: `headline-display`, `headline-lg`, `headline-md`, `body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`
- **Rounded**: `none`, `sm`, `md`, `lg`, `xl`, `full`

## Consumer behavior for unknown content

| Scenario | Behavior |
|---|---|
| Unknown section heading | Preserve; don't error |
| Unknown color token name | Accept if value valid |
| Unknown typography token name | Accept |
| Unknown spacing value | Accept; store as string if not a valid dimension |
| Unknown component property | Accept with warning |
| Duplicate section heading | Error; reject file |

## Minimal valid example

```md
---
name: Heritage
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
typography:
  headline-lg:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: 4px
  md: 8px
spacing:
  sm: 8px
  md: 16px
---

## Overview
Architectural minimalism meets journalistic gravitas — a premium matte finish.

## Colors
- **Primary (#1A1C1E):** Deep ink for headlines and core text.
- **Tertiary (#B8422E):** "Boston Clay" — the sole driver for interaction.

## Do's and Don'ts
- Do use the tertiary color for only the single most important action per screen.
- Don't mix rounded and sharp corners in the same view.
```
