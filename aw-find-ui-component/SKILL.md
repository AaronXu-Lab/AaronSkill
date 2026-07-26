---
name: aw-find-ui-component
description: Find and compare equivalent Base UI ecosystem components across the curated shadcn/ui Base, coss ui, Dice UI Base, ReUI public MIT, and exaBase Design System catalogs, while reporting incompatible variants and license provenance. Use when asked to find a component, compare implementations, browse component references, identify a Base UI alternative, or search beyond the curated catalogs before choosing a component to port into AXO.
---

# AW Find UI Component

Find references before implementing. Return comparable preview and source addresses; do not install or port anything during discovery.

## Refresh Before Every Query

Run the refresh script from this Skill directory before searching:

```bash
python3 scripts/refresh_catalogs.py --json
```

Read the returned source statuses. Continue with cached entries when a source is `stale`, disclose the stale source in the result, and report a source as unavailable when it has no usable cache.

The curated catalogs contain only verified Base UI or compatible native React/HTML variants:

- shadcn/ui Base variants
- coss ui components and particles
- Dice UI Base variants
- ReUI components and examples that are present in the public MIT GitHub repository
- exaBase Design System V4 registry components

Apply these source-specific license boundaries:

- Treat only files confirmed in the public `keenthemes/reui` repository as ReUI MIT material. Exclude Pro/Ultimate blocks, icons, templates, authenticated registry output, paid MCP output, or any item that cannot be traced to the public repository.
- Treat exaBase snippets as mixed provenance: upstream shadcn/ui portions are MIT, while ExaWizards changes and additions are CC BY 4.0. Report both, require attribution plus a modification note for copied ExaWizards material, and prefer the upstream shadcn/ui source when the implementation is materially identical.

Do not silently add other libraries or non-Base variants.

## Interpret and Search

1. Resolve the requested behavior before matching a name. Distinguish ambiguous terms such as chat message, toast message, alert, and validation message.
2. Read `references/component-aliases.md` when the request uses an alternate name or describes behavior instead of a component name.
3. Search the local catalog with the original query and any useful aliases:

```bash
python3 scripts/search_catalogs.py --query "<component>" --alias "<alternate term>" --json
```

4. Audit the same library's official documentation when a curated source has no exact or equivalent match, or when its best result is an unrelated fuzzy match. Check whether the requested component exists under an excluded variant such as Radix. This is a same-library exclusion audit, not a search for additional libraries.
5. Record excluded same-library matches separately with the exact library, component, variant, preview URL, and exclusion reason. Do not recommend or port them as Base UI candidates.
6. Verify promising preview pages and exact source before recommending them. Treat live documentation and exact variant source as authoritative over cached descriptions.
7. For ReUI, verify that the exact source exists in the public GitHub repository and link that file or directory. Never use an authenticated registry response as open-source evidence.
8. For exaBase, inspect the exact registry item for Base UI, native React/HTML, or allowed non-primitive dependencies. Record shadcn MIT plus ExaWizards CC BY 4.0 unless the selected code is demonstrably unchanged upstream shadcn code.
9. Rank exact matches first, semantic equivalents second, and useful compositions last. Prefer the smallest component that satisfies the described behavior.

## Return the Comparison

Always account for every curated library. Scope negative results as `No eligible Base match`; never say that the library has no such component unless the same-library exclusion audit also found nothing. Use this compact shape:

| Library | Component | Match | Preview | Source | License / provenance | Base UI evidence | Verified |
|---|---|---|---|---|---|---|---|

Use `Exact`, `Equivalent`, or `Composite` for matches. Mention stale or unavailable catalogs immediately below the table. Recommend one result only when the fit is materially clearer; the user remains responsible for choosing the source.

When the exclusion audit finds a component, add this compact table immediately after the main comparison:

| Library | Component | Excluded variant | Preview | Exclusion reason |
|---|---|---|---|---|

Describe the outcome as, for example, `Dice UI has Data Table, but only the Radix variant was found; Dice UI Base has no eligible match.` Keep excluded results visible for accuracy, but do not mix them into eligible recommendations.

## Search Beyond the Curated Catalogs

Search the web only when the user explicitly asks for more libraries or results outside the curated set.

For each newly discovered library:

1. Verify the official documentation and repository.
2. Verify the exact component variant imports `@base-ui/react`, composes verified Base UI components, or uses compatible native React/HTML without another primitive framework.
3. Reject Radix-only, React Aria, Ark UI, Headless UI, and other competing primitive implementations.
4. Check the license, maintenance activity, working preview, and machine-readable catalog or stable documentation index. Keep public open-source and paid/proprietary distribution channels separate.
5. Present the library as a candidate. Add it to `references/sources.json` only after the user explicitly approves it, then refresh the catalog.

## Offer the Port Handoff

Wait until the user selects an eligible result. Detect `aw-port-axo-ui-component` from the available Skill catalog or standard user/project Skill directories. If installed, ask whether to port the selected component; never invoke it automatically.

Pass this handoff when the user agrees:

```yaml
library: <library>
component: <name>
variant: base
foundation: base-ui
preview_url: <url>
source_url: <url-or-null>
dependencies: <known-dependencies>
license: <verified-license-or-unknown>
base_ui_evidence: <exact evidence>
```

The Port Skill must revalidate the exact source and project constraints before implementation.
