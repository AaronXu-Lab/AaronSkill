---
name: aw-design-token-consistency-auditor
description: Audit design-token consistency across any two or all three of Figma Variables, DESIGN.md YAML, and CSS/Less tokens. Use to identify missing sources, missing or source-only tokens, value mismatches, canonical collisions, and unresolved references, and to generate stable Markdown, JSON, and CSV audit artifacts.
metadata:
  author: aaron_xu
  version: "1.0"
  creation_context: "为比较 Figma Variables、DESIGN.md 与 CSS/Less Token 的覆盖、映射和值一致性而创建，输出可供后续修复使用的结构化审计结果。"
---

# AW Design Token Consistency Auditor

Compare any two or all three supported sources. Produce evidence and repair inputs; do not rewrite source tokens automatically.

## Sources

Supported source keys are:

- `figma`: compact Figma Variables JSON from the relevant token collections.
- `design_md`: YAML frontmatter from `DESIGN.md`.
- `css`: CSS/Less variables, separated into source tokens, aliases, bridge aliases, and implementation variables.

Require at least two distinct source keys. The three valid pairs are `figma,design_md`, `figma,css`, and `design_md,css`; all three may also be selected.

Default project paths remain encoded in `scripts/audit_design_tokens.py`. User-provided paths always take precedence.

## Workflow

1. Confirm the selected two or three sources and their paths or URLs.
2. For Figma, export a compact JSON payload containing variable `name`, `resolvedType`, `collectionName`, and first-mode `value`. Include only `Design Tokens`, `Typography DT`, and `Components DT`; exclude `Other` from counts.
3. Read `references/token-normalization.md` and `references/platform-value-mapping.md` before interpreting values or changing mappings.
4. Run `scripts/audit_design_tokens.py` with `--sources` and the selected inputs.
5. Validate every artifact against `references/output-schema.md`.
6. Summarize counts in Chinese-first labels and link the Markdown, JSON, and CSV files.

Example:

```bash
python3 scripts/audit_design_tokens.py \
  --sources figma,design_md \
  --figma-json /path/to/figma-variables.json \
  --design-md /path/to/DESIGN.md \
  --out /path/to/reports
```

## Comparison Rules

- Preserve raw names and values; normalize only for comparison.
- Resolve CSS `var(...)` aliases before comparison.
- Compare only canonical CSS source tokens; exclude public aliases, bridge aliases, and implementation variables from coverage counts.
- Normalize hex case, whitespace, known units, Figma percentage letter spacing, and Figma opacity percentages.
- Equal values alone do not prove semantic equivalence; uncertain mappings remain explicit.
- A token present in one source only is `source_only_token`, not automatically an error.
- A token shared by selected sources but absent from another selected source is `missing_token`.

Issue keys are fixed: `missing_source`, `missing_token`, `source_only_token`, `value_mismatch`, `duplicate_canonical`, and `unresolved_reference`.

## Output Contract

Always write all three artifacts:

- `token-audit.json`: authoritative structured result following `references/output-schema.md`.
- `token-audit.csv`: flat issue rows for spreadsheets.
- `token-audit.md`: human-readable sources, counts, issue groups, and repair prompt.

The JSON schema version is `1.0`. Keep every issue in the single `issues` array with stable `type`, `severity`, `canonical`, `details`, and `sources` fields. The selected source list and per-source status must remain explicit so a two-source audit cannot be mistaken for a three-source audit.

## Interpretation Priority

1. Missing or unreadable sources.
2. Shared semantic value mismatches.
3. Missing tokens expected across selected sources.
4. Source-only tokens requiring human judgment.
5. Mapping improvements for systematic naming differences.

Never recommend deletion solely because a token is source-only.

## Figma Repair Note

When repairing the project-specific font-family variables, use `references/update-figma-font-family-aliases.js`. Keep the concrete `Typography DT` font stack aligned with DESIGN.md/CSS while style-level Figma variables may alias to the runtime font-family variable.
