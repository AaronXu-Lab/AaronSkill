# Platform Value Mapping Reference

Use this reference when comparing token values that have the same meaning but different platform encodings. These rules are applied after name normalization and before reporting `value_mismatch`.

## Typography

### Letter Spacing

Figma stores typography letter spacing as a percentage-like numeric value.

DESIGN.md and CSS often store the same value as `em`.

Treat these as equivalent:

- Figma `2` -> DESIGN.md/CSS `0.02em`
- Figma `0` -> DESIGN.md/CSS `0` or `0em`
- Figma `-1` -> DESIGN.md/CSS `-0.01em`

Comparison rule:

```text
figma_letter_spacing_number / 100 == em_value
```

When reporting values, preserve the raw source values. Only use this conversion for equivalence checks.

### Font Size and Line Height

Figma commonly exports font sizes and line heights as unitless numbers. DESIGN.md and CSS often store them as `px`.

Treat these as equivalent:

- Figma `16` -> DESIGN.md/CSS `16px`
- Figma `24` -> DESIGN.md/CSS `24px`

Comparison rule:

```text
unitless_number == px_value
```

### Font Weight

Treat numeric font weights as equivalent whether they are parsed as strings or numbers:

- `400` == `"400"`
- `500` == `"500"`

## Spacing, Size, and Radius

Figma numeric variables for spacing, dimensions, and corner radius are unitless values in pixels. DESIGN.md and CSS usually store them with `px`.

Treat these as equivalent:

- `spacing/md`: Figma `20` -> DESIGN.md/CSS `20px`
- `rounded/md`: Figma `8` -> DESIGN.md/CSS `8px`
- `size/control-md`: Figma `40` -> DESIGN.md/CSS `40px`

Comparison rule:

```text
unitless_number == px_value
```

## Opacity

Figma `OPACITY` variables are stored as percent-like numeric values, while DESIGN.md and CSS should store the same opacity as a decimal number.

Treat these as equivalent:

- Figma `40` -> DESIGN.md/CSS `0.4`
- Figma `100` -> DESIGN.md/CSS `1`
- Figma `0` -> DESIGN.md/CSS `0`

Comparison rule:

```text
figma_opacity_number / 100 == decimal_opacity_value
```

When reporting values, preserve the raw source values. Only use this conversion for equivalence checks. For example, keep Figma `opacity/disabled` displayed as `40` if that is the stored variable value, but compare it as actual opacity `0.4`.

## Token References and Aliases

Figma Variables can store references as `VARIABLE_ALIAS` objects. The compact Figma export should include both the alias `id` and the target variable `name`.

Treat these reference encodings as equivalent after canonical name normalization:

- Figma alias target `color/primary` == DESIGN.md `{colors.primary}`
- Figma alias target `rounded/full` == DESIGN.md `{rounded.full}`
- Figma alias target `size/control-md` == DESIGN.md `*size-control-md`
- Figma alias target `Font Family` in `Other` Collection == DESIGN.md `{typography.fontFamily}` when the audited token canonical key is under `typography/*/font-family`

Comparison rule:

```text
alias:<figma target name> == {design.md.reference} == *yaml-anchor-reference
```

Preserve raw values in reports. Only use this conversion for equivalence checks.

### Figma Font Family Runtime Exception

Figma has trouble recognizing comma-separated font family stacks when they are bound directly from a string variable in `Typography DT`. Keep `typography/font-family` and the nested `typography/*/font-family` variables in `Typography DT` so Figma, DESIGN.md, and CSS still have matching audit coverage.

`Typography DT` `typography/font-family` is the audit-alignment token. It must keep the concrete comma-separated font stack from DESIGN.md/CSS, even if it is not used directly by Figma text bindings.

For actual Figma usage, style-level `Typography DT` variables whose names end with `/font-family`, such as `typography/body-md/font-family`, should alias to `Other` Collection's `Font Family` variable. The `Other` Collection remains excluded from audit counts, but this specific alias target is treated as equivalent to `typography.fontFamily`.

Add a description to `Typography DT` `typography/font-family`:

```text
Audit alignment token: keep this value as the DESIGN.md/CSS comma-separated font stack. For actual Figma text binding, route style-level typography/*/font-family variables to Other/Font Family.
```

Add a description to style-level `Typography DT` font-family variables:

```text
Figma runtime note: this style-level token aliases to Other/Font Family because Figma may not recognize comma-separated font family stacks from Typography DT string variables. The root typography/font-family token stays as the DESIGN.md/CSS-aligned font stack for audit coverage.
```

## Floating Point Noise

Figma can return floating point values with extra precision.

Treat near-equal numeric values as equivalent when their absolute difference is less than `0.0001`.

Examples:

- `0.9700000286102295` == `0.97`
- `12.0000001` == `12`

Preserve raw values in reports; only suppress mismatches when normalized values are equivalent.

## What Not To Normalize

Do not silently equate values with different semantics:

- `%` and `px`
- `rem` and `px`
- colors with different alpha values
- timing functions with different curves
- shadows with different offsets, blur, spread, or alpha

If a conversion is not listed here, report the mismatch or mark it as a mapping-rule review item.
