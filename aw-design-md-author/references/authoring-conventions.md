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
- Components prose covers selection, hierarchy, visual states, composition, and semantic misuse. Keep state machines, events, props, and APIs outside the contract; see Visual states and composition below.
- Write Do's and Don'ts last, using observed bad outcomes rather than generic UX advice.

## Design intent

Review whether the contract connects **design intent → visual treatment → applicable conditions → observable result**. Use this as a reasoning aid, not four mandatory fields per rule. A stated quality such as “compact” or “editorial” needs enough concrete relationships to guide a new design: where density changes, what carries emphasis, and what stays subordinate.

For example, “compact and efficient” alone leaves layout choices open. A supported rule might say: “Use the dense spacing tier between comparable data rows; keep group headings separated with the group-spacing role so users can distinguish groups while scanning.” Reference the project's actual roles; this example does not establish new tokens or values.

Preserve the user's intent and voice. Flag adjectives with no corresponding decisions, and decisions that undermine stated priorities. Suggest options when the project has not settled a choice; do not manufacture dimensions, ratios, or breakpoints to make the prose sound precise. Prose can state observable visual relationships that are not representable in the token schema, while exact token values remain in their owning layer.

## Layout and media

Use the relevant dimensions below when authoring or reviewing Layout, Shapes, and Components. Extend existing subsections where useful; neither new top-level sections nor a fixed checklist in the output are required.

- **Composition and density:** distinguish container width from reading width; explain alignment, gutters, grouping, and where dense comparison or spacious presentation applies. A spacing scale alone does not define page composition.
- **Responsive changes:** describe what reorders, stacks, hides, scrolls, or stays reachable as available space changes. Breakpoint numbers alone are insufficient. Preserve established content priority and distinguish decorative simplification from removing information or actions.
- **Content variation:** cover relevant long headings, labels, lists, or empty content with wrapping, truncation, overflow, or layout rules where the contract owns these decisions. Do not invent application behavior.
- **Media treatment:** where imagery contributes to the design, describe aspect ratio, crop focus, framing, text overlays, and narrow-screen treatment. Distinguish product captures that must remain legible from atmospheric images that can be cropped more freely.

Only include rules supported by the target system and relevant to the request. For instance, a side panel becoming a bottom action area is a possible responsive choice, not a universal mobile pattern. Missing evidence is a reportable gap, not permission to invent a transformation or extract another website.

## Visual states and composition

Describe the visual distinctions needed for the component's applicable states: hover, keyboard focus, selected, pressed, disabled, error, or loading. Include only relevant, established states; do not require every component to implement a full matrix. A source's inability or policy not to capture hover does not prohibit documenting supported hover styling in the target contract.

Explain which role or treatment changes and which remains stable, including meaningful differences between focus, selection, and error. Keep exact values in the owning layer; use the existing component-token convention when the document owns them. Do not copy component internals into a code-backed contract merely to fill gaps.

For composition, specify relevant relationships among icon, label, supporting text, and container: alignment, relative emphasis, spacing roles, and how the group handles content growth. Describe observable presentation, not event handling or API behavior. State and composition guidance should let a reader extend a component without guessing its visual grammar.

## Semantic consistency

Compare the same role across YAML, Overview, token explanations, component descriptions, responsive rules, and Do's and Don'ts. Check values and resolved references, intended usage, applicable theme or viewport, state, and stated exceptions or category boundaries. This is a manual semantic review; lint success is not evidence that these claims agree.

First determine whether apparently different treatments belong to explicitly differentiated contexts. A pill marketing CTA and a compact rectangular navigation action can coexist when their roles are clear. “All buttons are pills” and “all buttons use the medium radius” without scope distinctions are a conflict.

For each meaningful conflict, identify both locations, the shared role, the conflicting claims, and the design choice it leaves ambiguous. Use an established authoritative decision to resolve it within the authorized scope. Do not silently choose the later passage, the more detailed passage, or a preferred exemplar. Normative YAML owns token values, but a discrepancy with prose may indicate a stale token or an unresolved visual decision; do not automatically rewrite the prose to conceal it.

In a narrow task, check related claims throughout the complete contract and change only affected, authorized content. Report unrelated conflicts separately. Review-only findings remain read-only; unresolved choices can be reported while other authorized work is completed.

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
