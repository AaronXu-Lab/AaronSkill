---
name: aw-find-and-port-ui-component
description: Find, compare, verify, and port UI component implementations through two strictly separated phases. Use Find to discover candidates and compare behavior, source, license, dependencies, and target-project compatibility without modifying code. Use Port only after the user explicitly selects an implementation or supplies an exact source, then adapt the smallest required behavior to the target project's existing components, conventions, technology stack, and optional DESIGN.md guidance.
metadata:
  author: aaron_xu
  version: "1.0"
  creation_context: "为将 UI 组件发现、比较、来源验证与项目移植整合为通用的两阶段工作流而创建，在保留用户明确选择门的同时，统一处理许可证、依赖兼容性、现有组件复用与目标项目风格适配。"
---

# AW Find and Port UI Component

Find references before implementing. Keep Find and Port as separate runs with an explicit user-selection gate between them. Never continue automatically from Find into Port.

## Choose One Phase

- **Find:** use when the user asks to find, compare, browse, or recommend component implementations. Return candidates and stop without modifying the target project.
- **Port:** use only when the user explicitly selects a Find result or supplies an exact source. Revalidate the source, adapt it to the target project, and verify the implementation.

If a request asks to find and implement in one turn, complete Find, present the comparison, and stop for an explicit selection. Do not add a combined or automatic mode.

## Shared Evidence Rules

- Resolve the requested behavior before matching a component name.
- Judge compatibility from the exact variant's source, imports, dependencies, runtime assumptions, and license—not from a library name.
- Treat cached descriptions and handoff metadata as leads. Verify the live preview and exact source before recommending or porting.
- Do not introduce a new component framework, runtime, or package without explicit user approval.
- Preserve required license notices. For restrictive or unknown licenses, do not copy protected source or styling; use only sufficiently documented observable behavior and accessibility contracts.
- Prefer the smallest implementation that satisfies the current behavior.

## Find Phase

### Refresh the Curated Catalogs

Run before every query:

```bash
python3 scripts/refresh_catalogs.py --json
```

Continue with cached entries when a source is `stale` and disclose it. Report a source as unavailable when it has no usable cache.

The bundled catalogs currently cover verified Base UI or compatible native variants from:

- shadcn/ui Base
- coss ui
- Dice UI Base
- ReUI material verified in its public MIT repository
- exaBase Design System V4
- Fluid Functionalism Base UI or compatible native variants

These are the current built-in discovery sources, not permanent compatibility judgments or requirements for the Port phase.

### Interpret and Search

1. Read `references/component-aliases.md` when the request describes behavior or uses an alternate name.
2. Search the original query and useful aliases:

```bash
python3 scripts/search_catalogs.py --query "<component>" --alias "<alternate term>" --json
```

3. Verify promising preview pages and exact source.
4. When a catalog lacks an eligible match, inspect the same library's current official variants and record any incompatible result separately with evidence. Do not generalize a variant-level incompatibility to the whole library.
5. For ReUI, accept only source traceable to the public repository; keep paid or authenticated distribution separate.
6. For exaBase, report upstream and ExaWizards provenance accurately. Require attribution and a modification note when copied material requires CC BY 4.0 treatment.
7. For Fluid Functionalism, prefer the Base UI registry item when both Base UI and Radix variants exist. Treat the catalog entry as a lead and verify the exact live registry item and its dependency graph before recommending or porting.
8. Rank exact behavioral matches first, semantic equivalents second, and useful compositions last.

Search beyond the bundled catalogs only when the user explicitly requests broader discovery. Verify each additional source's official documentation, repository, exact implementation, license, maintenance status, and target-project compatibility. Add it to `references/sources.json` only after the user approves maintaining it as a curated source.

### Return and Stop

Account for every curated source:

| Source | Component | Match | Preview | Source | License / provenance | Foundation evidence | Compatibility | Verified |
|---|---|---|---|---|---|---|---|---|

Use `Exact`, `Equivalent`, or `Composite`. Put incompatible exact variants in a separate table with their evidence and current incompatibility reason. Mention stale or unavailable catalogs directly below the tables.

Finish with:

```markdown
## Find Result
- Recommended: <candidate or none>
- Reason: <material fit>
- Trade-offs: <important differences or none>

## Next Action
Select one candidate explicitly before running the Port phase.
```

Do not install packages, edit the target project, or invoke Port automatically.

## Port Phase

### Require an Exact Selection

Proceed only when the user supplies one of:

- an explicitly selected Find result;
- an exact preview, registry, repository, or source URL;
- a precise local reference implementation.

Read `references/source-retrieval.md`, retrieve the exact implementation, and verify its imports, dependencies, license, behavior, and accessibility contract. Stop when the source is ambiguous or the requested behavior cannot be established safely.

### Establish the Target Project Contract

1. Find the repository root and current branch.
2. Read every applicable `AGENTS.md` and project instruction.
3. Locate the relevant application and UI code from repository evidence; do not assume a framework or directory layout.
4. Inspect the package manifest, lockfile, component conventions, exports, style system, icon library, tokens, tests, and closest existing implementation.
5. If `DESIGN.md` exists, read its owned visual rules and use them as style guidance. Respect code-owned implementation details when the document is code-backed.
6. Search shared and page-local components before writing. Prefer reusing or extending an existing component; do not create a duplicate merely to match an external name.

### Define and Implement the Minimum Scope

- Identify the real page and interaction that need the component.
- Decide whether the implementation belongs in the shared library or beside its first consumer, following current project conventions.
- Adapt behavior and accessibility to the project's existing framework and primitives.
- Use the project's current styling method, tokens, icon library, naming, state patterns, and public API conventions.
- Treat the external implementation as behavioral and structural evidence, not as the target project's visual authority.
- Remove unsupported machinery, speculative variants, providers, or abstractions without a current requirement.
- Record unavoidable new dependencies and hardcoded visual values. Obtain explicit approval before adding a package or foundational UI system.

Ask the user only when a choice changes visible behavior, public API, data contract, dependency set, or another material project contract.

### Validate Proportionally

Inspect available scripts before selecting commands:

1. Run the available type or compile check for API changes.
2. Run relevant tests when present or when new logic merits focused coverage.
3. Inspect the target page or component gallery for meaningful UI changes, including relevant states and console errors.
4. Run the production build when configuration or bundling is affected or project instructions require it.
5. Report authentication, data, environment, or runtime boundaries exactly; do not present compilation as interaction verification.
6. Restore temporary mocks, logging, environment values, browser state, and viewport changes.

### Return the Port Result

```markdown
## Port Result
- Source: <selected implementation>
- Ported: <behavior and locations>
- Reused: <existing components and utilities>
- Adapted: <target-project compatibility changes>
- Omitted: <unneeded source complexity and why>

## Validation
- <command or visual check>: <result>
- Unverified: <exact boundary or none>

## Follow-up Trigger
- <observable condition that justifies omitted complexity, or none>
```
