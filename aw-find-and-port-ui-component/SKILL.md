---
name: aw-find-and-port-ui-component
description: Find and compare implementations for a concrete UI component, or adapt an explicitly selected component implementation into a target project. Use for component-level discovery or porting, not whole app, page, workspace, or generic file migration.
metadata:
  author: aaron_xu
  version: "1.7.0"
  creation_context: "为将 UI 组件发现、比较、来源验证与项目移植整合为通用的两阶段工作流而创建，在保留用户明确选择门的同时，统一处理许可证、依赖兼容性、现有组件复用与目标项目风格适配。"
---

# AW Find and Port UI Component

Discover suitable implementations or adapt a selected reference when the request centers on one concrete UI component.

Read the [workflow](references/workflow.md) first to apply the intent-and-granularity gate, select one phase and use its shared evidence, authorization and completion rules. Then read only the selected phase:

- [Find](references/find.md): discovery, comparison and recommendations; ends at explicit user selection.
- [Port](references/port.md): requested implementation of an explicitly selected candidate or exact source.

Do not trigger from the mere presence of a design branch, local reference source, copied files or a second application. Whole-app or page migration, workspace splitting and dual-app initialization stay in the project's ordinary workflow. A local or same-repository source remains eligible when the request identifies the exact component implementation and its target component.

An exact component URL supplied only for comparison remains Find. Ordinary local fixes without discovery or reference porting are outside this skill.

![UI component finding and porting workflow](docs/workflow.svg)
