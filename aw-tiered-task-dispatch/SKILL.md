---
name: aw-tiered-task-dispatch
description: "在 Codex 或 Claude 显式建立并使用一个主会话协调、三个模型档位的持久执行会话来派发项目任务。"
metadata:
  version: "1.5.0"
  author: "aaron_xu"
  creation_context: "为需要在主会话充分讨论后，按任务难度把项目实施交给不同模型档位的持久会话的重复协作需求而创建。"
---

# 分档任务派发

用户显式调用后，保留当前会话作为主会话。主会话直接完成讨论、资料查询、代码只读调查、盘点、解释和分析，即使需要调用工具也不派发。只在用户要求建立工作方式时创建三个项目执行会话；只有实际实施、修改或落地执行任务才选档派发。主会话不实现或独立复核已派发的实施任务；执行会话独立完成实施与必要校验。主会话的模型设置保持原样。

实施任务先按**当前任务**的剩余不确定性、影响范围和协调复杂度，从当前平台低档起评：Codex 为 Luna · high → Sol · medium → Astra · low；Claude 为 Sonnet · high → Opus · medium → Fable · low。再衡量关联历史是否能显著减少理解成本、衔接或迁移风险；同组件或原会话曾负责，不会自动升档或锁定原会话。简单后续任务可降档；正在执行的同一修改可为避免冲突留在原会话。不按代码量、文件数、校验需求或平均分配来选档。具体判断、派发模板和 [回归场景](tests/dispatch-routing.md)见相关文档。

执行前阅读 [分档任务派发工作流](references/workflow.md)，其中规定授权边界、会话复用、平台档位、派发内容和停止条件。使用当前平台实际可用的项目与会话工具，并先核对模型、强度和持久会话能力；若在 Codex，可用 `list_projects`、`list_threads`、`create_thread`、`send_message_to_thread`、`wait_threads` / `read_thread` 完成对应步骤。工具或配置不可用时报告受阻步骤，不假装已经创建或派发，也不自行替换模型。

![分档任务派发流程：讨论、建立档位、派发与回报](docs/workflow.svg)
