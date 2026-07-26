---
name: aw-port-axo-ui-component
description: Port a verified Base UI ecosystem component into the AXO app frontend as a minimal native implementation using its existing @base-ui/react primitives, CSS Modules, design tokens, and component conventions. Use when asked to introduce, adapt, or recreate a component from any library whose exact selected variant is built on Base UI or compatible native React/HTML, including after a handoff from aw-find-ui-component, without importing an external component package wholesale.
---

# AW Port AXO UI Component

Port the smallest behavior that satisfies the current AXO use case. Treat external libraries as implementation references, not dependencies or visual authorities.

## Establish the Current Project Contract

1. Find the repository root with `git rev-parse --show-toplevel` and check the current branch.
2. Read every applicable `AGENTS.md`. On branch `design`, also read the current `AGENTS.design.md`.
3. Locate the app frontend from repository documentation instead of assuming `front/`. In the current monorepo it is `axo-app-fe/`.
4. Before UI work, read the repository's `DESIGN.md`; on `design`, also read token-maintenance instructions and the actual theme/token files required by `AGENTS.design.md`.
5. Before adding or changing a shared component, read the current `src/components/ui/CONVENTIONS.md`, barrel, closest existing component, and component gallery registration.

Repository instructions and current code override examples in this Skill.

## Decide Whether to Port

1. Extract the requested component, exact variant, preview/source addresses, declared dependencies, license status, and any Base UI evidence from the user or Finder handoff.
2. Read `references/source-retrieval.md` and inspect the exact source. Verify imports and registry dependencies; library-level marketing or handoff metadata is not sufficient evidence.
3. Accept a variant only when it directly uses `@base-ui/react`, composes other verified Base UI components, or uses compatible native React/HTML without another primitive framework.
4. Reject Radix, React Aria, Ark UI, Headless UI, or another competing component framework. When the same library has a Base variant, redirect to that exact variant; otherwise stop and explain the mismatch.
5. Verify the source license before adapting code. Preserve required notices. For a restrictive or unknown license, do not copy source or styling; recreate only clearly documented observable behavior and accessibility contracts, or stop when those contracts are insufficient.
6. Search the AXO UI barrel, component folders, page-local components, and pending-component register before writing.
7. Reuse or extend an existing component when its public contract already fits. Do not create an alias component solely to match an external name.
8. Port only when the behavior can be expressed with installed primitives, native React/HTML, and existing project utilities without adding a component framework.
9. Stop and explain the gap when the reference requires an unsupported dependency, an undefined product interaction, or new design tokens. Do not silently invent those contracts.

Repository source and current project constraints override Finder handoff metadata. Verify remote paths at execution time; upstream repository structures are not stable APIs.

## Define the Minimum Scope

Identify the real page and interaction that need the component. Keep the public surface limited to current observable requirements.

Remove unsupported or unnecessary machinery such as virtualization, infinite-history anchoring, multi-layer providers, speculative variants, or cross-page state. Preserve it only when the current task supplies a concrete requirement or scale condition.

State the intended port briefly: behavior retained, complexity omitted, and reason. Continue autonomously when this is a straightforward implementation choice. Ask the user only when the choice changes visible behavior, public API, data contract, or required dependency.

## Choose the Landing Point

- Put a broadly reusable primitive or composed control in `src/components/ui/<Name>/` using the current conventions.
- Put page-bound behavior in `src/pages/<domain>/` or its local `components/` directory.
- If reuse is plausible but not yet proven and repository instructions require review, add it to the pending-component register and keep the first implementation local.

For shared components:

- use `<Name>/index.tsx` and `<Name>/<Name>.module.css`;
- export from the UI barrel in its required order;
- add or update the gallery only when the public API, visible states, or existing examples would otherwise be incomplete or misleading.

## Implement in the AXO System

- Prefer installed `@base-ui/react/<primitive>` subpaths for interactive foundations. Native or CSS-only implementations are valid when that matches existing project conventions.
- Do not add Radix or another UI framework. Add any dependency only with explicit user approval.
- Use `@phosphor-icons/react` and first search for an existing icon choice.
- Replace Tailwind classes with CSS Modules and verified existing tokens.
- Treat `DESIGN.md` and current token files as the visual authority. Implement only the states and properties they define; do not import the source library's visual language.
- Preserve controlled/uncontrolled names used by Base UI and the local library.
- Forward supported native props and `className`; require accessible names for icon-only controls.
- Follow current local TypeScript naming and component patterns rather than generic examples in this Skill.
- Keep frequently changing, non-rendering values in refs; avoid providers, hooks, or abstractions without a current consumer.
- Record every unavoidable hardcoded visual value in the final result.

## Validate Proportionally

Inspect the frontend `package.json` and lockfile before selecting commands. Do not claim scripts such as lint or test exist when they do not.

1. Run the available typecheck for TypeScript/API changes.
2. Run relevant tests when the project has them or when new pure logic merits focused coverage.
3. For a new component or meaningful interaction, run the dev server and inspect the component gallery or target page, including console errors and relevant states.
4. Run the production build for build/configuration risk or when repository instructions require it.
5. If authentication, backend data, or environment state blocks live behavior, report the exact unverified boundary. Do not present compilation as interaction verification.
6. Restore temporary mocks, environment values, logging, browser state, and viewport changes.

## Finish

Perform a local simplicity pass; Ponytail is optional, not a dependency. Check for duplicate components, new packages, speculative API, redundant wrappers, unused variants, hardcoded tokens, and temporary state.

Return:

```markdown
## Result
- Ported: <behavior and locations>
- Reused: <existing AXO primitives/components>
- Omitted: <source complexity intentionally excluded and why>

## Validation
- <command or visual check>: <result>
- Unverified: <exact boundary or none>

## Follow-up Trigger
- <observable condition that justifies omitted complexity, or none>
```
