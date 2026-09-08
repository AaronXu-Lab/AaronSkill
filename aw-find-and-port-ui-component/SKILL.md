---
name: aw-find-and-port-ui-component
description: Find and compare UI component implementations, or port an explicitly selected candidate or exact reference source into a target project.
metadata:
  author: aaron_xu
  version: "1.2.1"
  creation_context: "为将 UI 组件发现、比较、来源验证与项目移植整合为通用的两阶段工作流而创建，在保留用户明确选择门的同时，统一处理许可证、依赖兼容性、现有组件复用与目标项目风格适配。"
---

# AW Find and Port UI Component

Discover suitable implementations or adapt a selected reference to the target project.

Read the [workflow](docs/workflow.md) to select one phase and apply its shared evidence, authorization and completion rules. Then read only the selected phase:

- [Find](references/find.md): discovery, comparison and recommendations; ends at explicit user selection.
- [Port](references/port.md): requested implementation of an explicitly selected candidate or exact source.

An exact URL supplied only for comparison remains Find. Ordinary local fixes without discovery or reference porting are outside this skill.

![UI component finding and porting workflow](docs/workflow.svg)
