# DESIGN.md Authoring Conventions

## Canonical schema reminders

- Frontmatter is flat: `colors.primary`, `typography.body-md`, `rounded.md`, `spacing.md`, and optional `components.button-primary`.
- References use `{path.to.token}` and must resolve to primitives, except component properties may reference composites such as `{typography.label-md}`.
- Component properties include `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, and `width`.

## Naming

- Name tokens by abstract intent, not appearance or usage site: `surface-sunken`, not `sidebar-bg`; `emphasize-static`, not `viewport-shadow`.
- Prefer portable semantic names: `primary`, `secondary`, `surface`, `on-surface`, `error`; `headline-lg`, `body-md`, `label-sm`; `none`, `sm`, `md`, `lg`, `xl`, `full`.
- Avoid product or brand names in body prose. Frontmatter `name` and `description` may identify the system.
- Abstract the common trait instead of enumerating every component or screen where a rule applies.
- Express conditions as positive category rules instead of “X, except in Y.”
- Stop after positive definitions establish a distinction; do not append redundant corrective negations.

## Prose

- Tokens state what the system looks like. Prose explains when and why to use it.
- Keep every sentence tied to this system. If a paragraph can be pasted unchanged into any design system, remove it.
- Components prose covers selection, hierarchy, and semantic misuse—not state machines, events, props, or APIs.
- Write Do's and Don'ts last, using observed bad outcomes rather than generic UX advice.

## Ownership

- Standalone systems define exact component appearance and relevant states under `components:`.
- Code-backed systems keep component-exact values in code and promote only stable shared semantics into `DESIGN.md`.
- Generated projections are edited at their source and regenerated; never maintain two authorities.
- Never reverse-document incidental CSS as a normative decision.

## Multi-theme systems

- The official schema has no canonical `themes:` object. Do not invent one.
- Keep semantic names and key parity stable across themes.
- Store the explicitly selected default theme in `DESIGN.md`; validate other modes in their owning artifact.
- If portable theme documents are needed, define a project convention and label it as such.
