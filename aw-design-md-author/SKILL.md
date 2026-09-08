---
name: aw-design-md-author
description: Create, review, and maintain Google-format DESIGN.md contracts, including deferred TODO annotations.
metadata:
  author: aaron_xu
  version: "1.5.1"
  creation_context: "为按照 Google Labs DESIGN.md 官方规范完整创建、审查和维护设计系统文档而创建，统一处理 Token 所有权、语义命名、章节结构与验证。"
---

# AW DESIGN.md Author

Create and maintain a verifiable visual contract in the user's language, preserving their design intent and voice. Use for DESIGN.md work; extracting websites, screenshots, Figma or code is outside this skill.

Start with the [execution workflow](docs/workflow.md) to select the task, editing source, protection checks and completion criteria. Read only the relevant references below; reuse current guidance already read in this conversation.

## Task routing

| Task | Supporting guidance |
| --- | --- |
| Create a contract | [Official schema and sections](references/spec-summary.md), [authoring conventions](references/authoring-conventions.md), [validation](references/lint-rules.md) |
| Maintain or review a contract | Workflow plus affected convention sections; consult schema when schema is involved and validation when checking. Narrow requests still inspect the complete contract without authorizing unrelated edits. |
| Record deferred design or implementation TODOs | [Annotation mode](references/annotation-mode.md); contract edits remain normative maintenance |
| Rename or migrate spacing | [Tier naming, resolved-value mapping and migration acceptance](references/authoring-conventions.md#spacing-tiers-and-migration) |
| Edit or review body prose | [Prose rules](references/authoring-conventions.md#prose) and [body-boundary examples](references/authoring-conventions.md#body-boundary-examples) |
| Validate only or diagnose lint | [Protection gate, official rules and unavailable-validation handling](references/lint-rules.md) |

For creation examples, choose [standalone](references/example-full.md) or [code-backed](references/example-code-backed.md) as needed. Consult [exemplar patterns](references/exemplar-patterns.md) for design judgments, not default tokens.

## Essential boundaries

Reviews remain read-only. Editing source selection is internal; formal body prose stays about design. Preserve established scope and authorization, unrelated content and pending TODOs. Annotation changes protect the existing contract; migrations preserve resolved values unless visual change is authorized. Lint establishes only its checked gates, not visual quality or semantic compliance. Detailed rules and recovery paths live in the linked workflow and references.

![DESIGN.md authoring, maintenance and review workflow](docs/workflow.svg)
