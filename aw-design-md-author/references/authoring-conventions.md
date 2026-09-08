# DESIGN.md Authoring Conventions

## Naming

- Name tokens by abstract intent, not appearance or usage site: `surface-sunken`, not `sidebar-bg`; `emphasize-static`, not `viewport-shadow`.
- Prefer portable semantic names: `primary`, `secondary`, `surface`, `on-surface`, `error`; `headline-lg`, `body-md`, `label-sm`; `none`, `sm`, `md`, `lg`, `xl`, `full`.
- Avoid product or brand names in body prose. Frontmatter `name` and `description` may identify the system.
- Abstract the common trait instead of enumerating every component or screen where a rule applies.
- Express conditions as positive category rules instead of “X, except in Y.”
- Stop after positive definitions establish a distinction; do not append redundant corrective negations.
- Do not use prose to hide an exact visual decision missing from its owning layer, or add generic “follow the tokens” sections.

## Spacing tiers and migration

This Skill defaults to size tiers (`2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`) for space / spacing names. Keep pixel magnitudes in token values; avoid names such as `space-2` and `space-12`. `2xs` and `2xl` denote relative tiers, not pixel counts. Preserve established semantic roles such as `viewport-inset`. This preference is not an official Google schema restriction and does not authorize silently renaming an existing contract.

Choose the scale for the project. The existing full and code-backed examples intentionally use different values. A compact project's seven-tier example is:

```yaml
spacing:
  2xs: 2px
  xs: 4px
  sm: 6px
  md: 8px
  lg: 12px
  xl: 16px
  2xl: 20px
```

Seven tiers and these values are illustrative, not a universal scale. A CSS implementation may expose these as `--spacing-2xs` through `--spacing-2xl`; preserve the project's chosen export convention.

Before migrating, inventory definitions and consumers and map by original resolved value:

| Old token | Old value | Target token | Target value |
| --- | --- | --- | --- |
| xs | 2px | 2xs | 2px |
| sm | 6px | sm | 6px |
| md | 8px | md | 8px |
| lg | 12px | lg | 12px |
| xl | 20px | 2xl | 20px |

Only after accounting for existing usages introduce new `xs: 4px` and `xl: 16px`. A global redefine of `xs` or `xl` would change layout. For example, an old `calc(var(--spacing-xs) * 2)` resolves to 4px and must become `calc(var(--spacing-2xs) * 2)`, still 4px. An old `var(--spacing-xl)` becomes `var(--spacing-2xl)`, still 20px. Avoid chained replacements that rewrite newly migrated names.

Verify definitions, all affected calls, calculation results, generated exports and consuming packages together. Compare resolved values and affected layouts before and after; separate any explicitly authorized visual changes. Searches are supporting evidence: `xs` and `xl` legitimately remain with new meanings, so zero old-name matches cannot be the sole acceptance criterion. Work in other repositories only when authorized.

When the contract is settled but implementation remains elsewhere, retain a standalone comment near the owning spacing key, adapted to known evidence:

```yaml
# TODO(DESIGN): Implementation migration pending; the spacing contract is settled.
# Scope: token package CSS exports and app spacing consumers (record actual paths).
# Old xs=2px -> 2xs; old xl=20px -> 2xl; sm/md/lg retain their values.
# New xs=4px and xl=16px are for intentional new usages.
# Deferred because consumer migration is outside this document update's scope.
# Accept when definitions, calls, calculations, exports and consumers match this
# contract, existing resolved spacing/layout is preserved, and affected views
# are verified. Record contract version and remaining paths; remove only then.
```

Use known versions and paths instead of inventing them. Distinguish this implementation TODO from a pending design decision. Updating normative values/keys requires Normative Contract Mode; adding only a TODO for an already settled contract uses the annotation protection gate without a contract version bump.

## Prose

- Tokens state what the system looks like. Prose explains when and why to use it.
- Keep the formal body limited to applicable design language, token semantics, visual rules, component selection, and design rationale. Omit document duties, ownership-mode introductions, code/document responsibility splits, specific projects, repository/subproject names, paths, API ownership, and engineering workflows.
- Preserve legitimate frontmatter identity fields such as `name` and `description`. Keep engineering evidence in a separate report; requested TODO annotations may retain paths and migration traceability. Do not hide excluded responsibility statements in ordinary comments.
- Keep every sentence tied to this system's design decisions. If a paragraph can be pasted unchanged into any design system, remove it.
- Components prose covers selection, hierarchy, and semantic misuse—not state machines, events, props, or APIs.
- Write Do's and Don'ts last, using observed bad outcomes rather than generic UX advice.

## Multi-theme systems

- The official schema has no canonical `themes:` object. Do not invent one.
- Keep semantic names and key parity stable across themes.
- Store the explicitly selected default theme in `DESIGN.md`; validate other modes in their owning artifact.
- Describe theme applicability in design language only: for example, “The palette uses light surfaces; semantic roles retain the same meaning in dark mode.” Include only supported design decisions.
- If portable theme documents are needed, define a project convention and label it in the separate delivery report, not the formal body.


## Body boundary examples

These are authoring/review examples, not sections to copy wholesale into `DESIGN.md`.

| Input or candidate | Expected treatment |
| --- | --- |
| “This is a code-backed contract. The component library owns internals and APIs; this document maintains shared semantics.” | Remove the responsibility declaration from the artifact. Use ownership internally to locate the editing source; report it separately only if useful. |
| “These colors apply to light mode; the dark theme is maintained in the application repository's theme file.” | Retain only the supported design scope: “These colors apply to light mode.” Add dark-mode semantic or visual rules only when established. |
| “Use subtle surface contrast for inset content so dense groups stay distinguishable without heavy borders.” | Keep: applicable visual rule with a design reason. |
| A concrete repository name, source path, or API owner embedded in component-selection prose | Remove the engineering detail from formal prose; preserve needed evidence in a separate report. Do not substitute another project's name. |
| Valid frontmatter `name` identifying the design system | Preserve: system identity metadata is allowed. Do not repeat a product name as a body title or project introduction. |
| User-requested `TODO(DESIGN)` with actual affected paths, settled migration mapping, and verification criteria | Preserve in standalone YAML/HTML comments under Annotation Mode; retain pending work until its existing resolution criteria are met. |

Review mixed paragraphs clause by clause: retain established visual meaning, remove document/engineering commentary, and do not invent replacement design rules merely to fill the gap. Do not relocate excluded declarations into ordinary HTML comments. Both bundled design examples use invented systems and values to show format; no example's brand, palette, or engineering context is a universal default.
