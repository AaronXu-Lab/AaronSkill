# DESIGN.md — Linter Rules (official `@google/design.md`, current CLI)

Run: `npx @google/design.md lint DESIGN.md` (JSON output; exit code 1 if any error). Nine rules:

| Rule | Severity | What it checks | How to fix while writing |
|---|---|---|---|
| `broken-ref` | **error** | A `{token.ref}` doesn't resolve to a defined token | Define the token, or correct the path. References must point to a primitive (except composite refs inside `components`). |
| `missing-primary` | warning | Colors defined but no `primary` color | Add a `primary` color; agents otherwise auto-generate one. |
| `contrast-ratio` | warning | A component's `textColor` on `backgroundColor` is below WCAG AA (4.5:1) | Darken/lighten one of the pair, or swap to a higher-contrast token. Surface to the user; don't silently change the palette. |
| `orphaned-tokens` | warning | A token is defined but never referenced by any component | If components are present, reference it where semantically correct or remove it if unused. If components are intentionally omitted in code-backed mode, do not add fake references; report the reduced lint coverage. |
| `missing-typography` | warning | Colors defined but no typography tokens | Add typography levels; agents otherwise fall back to default fonts. |
| `section-order` | warning | `##` sections are out of canonical order | Reorder to: Overview → Colors → Typography → Layout → Elevation & Depth → Shapes → Components → Do's and Don'ts. |
| `unknown-key` | warning | A top-level key looks like a typo of a known schema key | Correct genuine typos. Deliberate extension keys that do not resemble schema keys remain silent. |
| `token-summary` | info | Count of tokens per section | Informational. |
| `missing-sections` | info | Optional sections (spacing, rounded) absent while other tokens exist | Consider adding them. |

Also enforced by the parser: a **duplicate `##` section heading rejects the file** (treated as an error).

## Other useful CLI commands

```bash
npx @google/design.md spec              # full spec as markdown (inject into context)
npx @google/design.md spec --rules-only # just this rules table
npx @google/design.md diff A.md B.md    # token + prose diff; exit 1 on regression
npx @google/design.md export --format dtcg DESIGN.md         # → W3C DTCG tokens.json
npx @google/design.md export --format css-tailwind DESIGN.md # → Tailwind v4 @theme {}
npx @google/design.md export --format json-tailwind DESIGN.md# → Tailwind v3 theme.extend
```

Windows: if invoking from a `package.json` script, use the `designmd` alias (the `.md` bin name confuses Windows resolution). If `npm error ENOVERSIONS`, your npm registry isn't pointing at `https://registry.npmjs.org/`.

## Manual fallback checklist (if the CLI is unavailable)

1. Frontmatter is fenced by `---` at the very top and is valid YAML.
2. `name` present; `primary` color present; at least a few typography levels present.
3. Every `{ref}` resolves to a defined token; refs point to primitives (composite refs only inside `components`).
4. If components exist, review defined-but-unreferenced tokens; never invent component references in code-backed mode.
5. Each declared component `textColor`/`backgroundColor` pair ≥ 4.5:1 (normal text) / ≥ 3:1 (large). If components are omitted, run contrast checks against the actual component library instead.
6. `##` sections are in canonical order and none is duplicated.
7. Colors are valid CSS color strings; dimensions use `px`/`em`/`rem`.

## Coverage warning

A clean report validates only the content present in DESIGN.md. When `components:` is absent, the linter does not establish component contrast, state styling, alternate-theme parity, or accessibility. Require code-backed gallery/Storybook, visual-regression, contrast, and a11y checks for those concerns.
