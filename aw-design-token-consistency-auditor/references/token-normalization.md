# Token Normalization Reference

Use this reference when auditing or extending `audit_design_tokens.py`.

## Canonical Key Shape

Canonical keys use:

```text
group/name[/subname...]
```

Examples:

- `colors/primary`
- `colors/on-surface-muted`
- `rounded/md`
- `spacing/card-padding`
- `shadows/floating`
- `motion/fast`
- `typography/body-md/font-size`

## Source Naming Patterns

Figma commonly uses slash or collection names:

- `Color/Primary`
- `Colors/On Surface/Muted`
- `Radius/Md`
- `Spacing/Card Padding`
- `Typography/Body Md/Font Size`

DESIGN.md commonly uses nested YAML:

- `colors.primary`
- `colors.on-surface-muted`
- `rounded.md`
- `spacing.card-padding`
- `typography.body-md.fontSize`

CSS/Less commonly uses CSS custom properties:

- `--axo-primary`
- `--color-primary`
- `--axo-radius-md`
- `--radius-md`
- `--axo-spacing-card-padding`
- `--spacing-card-padding`
- `--axo-font-product`
- `--font-product`

## Group Synonyms

Normalize these group names:

- `color`, `colors`, `colour`, `colours` -> `colors`
- `radius`, `radii`, `rounded`, `border-radius` -> `rounded`
- `space`, `spacing`, `gap` -> `spacing`
- `shadow`, `shadows`, `elevation` -> `shadows`
- `type`, `font`, `fonts`, `typography` -> `typography`
- `motion`, `duration`, `ease`, `easing`, `transition` -> `motion`
- `size`, `sizes`, `dimension`, `dimensions` -> `size`
- `pattern`, `patterns`, `background` -> `patterns`

## CSS Prefix Rules

Strip implementation prefixes only for canonical comparison:

- `--axo-primary` -> `colors/primary`
- `--axo-radius-md` -> `rounded/md`
- `--axo-spacing-md` -> `spacing/md`
- `--axo-shadow-floating` -> `shadows/floating`
- `--axo-motion-fast` -> `motion/fast`

Keep the raw CSS variable name in reports.

## Alias Rules

CSS semantic aliases should resolve to their target value:

```css
--color-primary: var(--axo-primary);
```

Report both the raw value and the resolved value. If the alias target is missing, create an `unresolved_reference` issue.

## Value Comparison

Normalize values before comparing:

- lowercase hex colors
- convert Figma RGB objects in `0..1` format to hex
- remove quotes around simple string values
- collapse repeated whitespace
- remove extra whitespace after commas in color functions and shadows
- preserve meaningful units such as `px`, `em`, `%`, and timing functions

Do not compare comments, usage descriptions, or prose as token values.

## Platform-Specific Tokens

Some tokens are expected to be source-specific:

- CSS aliases that bridge app code to AXO tokens
- app-shell tokens such as card background, shell background, viewport shadow, scrollbar color
- Figma-only primitive palettes or component-only variables
- DESIGN.md-only documentation helpers

Flag these as `source_only_token`, not automatic errors.
