---
name: aw-figma-component-governance
description: Govern Figma component libraries through semantic naming, Variant and Property modeling, stable variant ordering, slot conventions, safe incremental edits, mandatory manual value-reordering instructions, and a structured audit attachment.
metadata:
  author: aaron_xu
  version: "0.2"
  creation_context: "为沉淀个人 Figma 组件库的命名、Variant 排序、Property/Slot 建模和人工调整规则而创建，减少组件治理中的重复判断。"
---

# AW Figma Component Governance

Inspect before editing, preserve visual styling unless redesign is requested, apply narrow changes, and validate after every meaningful write.

## Workflow

1. Inspect component/set names, properties, variants, direct children, internal layers, sizing, and current `componentPropertyDefinitions`.
2. Decide Variant versus Property boundaries before editing.
3. Apply semantic names and safe Variant-name ordering through narrow writes.
4. Re-read the component set and compare every `variantOptions` array with the target order.
5. Return the fixed `Manual Value Reordering` section.
6. Attach the structured JSON audit defined in `references/audit-schema.md`.

## Naming and Structure

- Component and owned layer names use Title Case with spaces.
- Families use ` / `, for example `Table / Header`; private helpers use `_`, for example `_Modal / Header`.
- Replace generated names such as `Frame 123`, `Variant2`, and `Property 1=Default` on owned nodes.
- Layers use semantic responsibility: `Leading Icon`, `Label`, `Description`, `Content Slot`.
- Variant and Property names use lowerCamel; Variant values use lowercase words.
- Boolean Variant values are `false, true`; optional internal content normally uses a Boolean Property named `show...`.
- Instance Swap Properties model replaceable icons or symbols.
- Slots model flexible compound content; keep visible Slot layer/property display names in Title Case when Figma couples them.
- Ignore inherited internals of external instances unless editing their source component.

## Variant Modeling

Use a Variant when a choice changes core structure, layout family, or state matrix. Use a Boolean Property for optional visibility and an Instance Swap Property for replaceable content. Prefer the smallest model that preserves structural meaning without variant explosion.

Variant name priority:

`size > style > type > width > content > trailing > position > align > count > selection > state > showClear > showHeader > selected > toggled > check > disable`

For unlisted names, order structural impact before visual state and enum choices before booleans.

Variant value rules:

- `none` first when it represents the baseline.
- Numeric values ascending; booleans `false, true`.
- Size: `large, medium, small`.
- Position: `top, left, right, bottom`.
- Type: `text, symbol, icon, symbol+text, icon+text`.
- State: `default, normal, hover, activate, active, loading, success, warning, error, disable`.
- Style: `ghost, tint, underline, outline, block, light, bordered, fill, destructive`.
- Insert uncovered values by semantic fit; regular choices precede destructive or special choices.

## Safe Figma Operations

- Read Variant definitions from the containing `ComponentSetNode`, not individual variant nodes.
- Load fonts before changing text or text-bound properties.
- Use stable node IDs and incremental writes, then re-read definitions.
- Do not rebuild a set solely to reorder value dropdowns unless the user explicitly accepts identity, publishing, and instance risks.
- The public Plugin API does not safely reorder existing `variantOptions` in place; unresolved value order requires manual dragging.

## Fixed Manual Value Reordering Section

Every final response must contain this exact heading, even when no action is needed:

```markdown
## Manual Value Reordering

### <ComponentSet name> (`<node-id>`)
- Property: `<variant property>`
- Current: `<value-1> → <value-2>`
- Target: `<value-2> → <value-1>`
- Action: In Figma's right sidebar, drag the values into the target order.
- Reason: The public Figma Plugin API cannot safely reorder existing `variantOptions` in place.
```

Repeat the subsection for every mismatch. If none exist, write exactly:

```markdown
## Manual Value Reordering

No manual value reordering is required.
```

Do not bury this section in a general summary or replace exact current/target arrays with prose.

## Structured Audit Attachment

Write or attach `component-governance-audit.json` following `references/audit-schema.md`. The Markdown answer and JSON attachment must agree on every manual reorder, rename, modeling decision, validation result, and unresolved risk.
