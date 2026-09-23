---
name: aw-canvas-design
description: 用可交互的实际组件画布设计和迭代多 Modal、Sheet、Dialog 业务流程，支持独立环境初始化、评论闭环与入口覆盖验收。不用于纯流程图或单个弹窗样式修改。
metadata:
  version: "1.2.6"
  author: "aaron_xu"
  creation_context: "源于在 ADM 画布中并列操作真实弹窗、分支与结果并通过评论迭代的实践，将可复用画布基础设施与多弹层业务设计分离，支持不同业务和技术栈。"
---

# Canvas Design

将多弹层流程放在同一可操作画布中，直接审阅组件、状态和分支。画布挂在所属业务页面路由下，形如 `/<业务路由>/design-canvas`（如 `/login/design-canvas`），`?preview={name}` 单独查看一条流程的实际效果。主流程负责业务设计；初始化模块只负责可复用承载环境，不在每次业务迭代时重建画布。

## 执行入口

先读 [执行工作流](references/workflow.md)，按任务选择资料：

| 当前任务 | 读取入口 |
| --- | --- |
| 只搭建环境，或发现现有能力缺失/失效 | [独立初始化模块](references/initialization.md)：检测复用、依赖与路由、隔离、操作、分层布局与连线精简；产出就绪记录 |
| 新流程或分支变化 | [流程建模](references/modeling.md)：实际入口、可达性、节点与覆盖表 |
| 实现或修改预览组件 | [场景设计](references/component-design.md)：实际组件、字段、滚动、Fake 与条件式步骤 |
| 搭建或调整卡片、目录、视口与图例 | [画布呈现规范](references/canvas-presentation.md)：以 [canvas-kit](assets/canvas-kit/) 为视觉与交互标准，有设计系统时用其组件与 token 实现同等效果 |
| 评论修改或明确要求业务迁移 | [评论与迁移](references/iteration-and-migration.md)：逐项闭环与授权边界 |
| 验收当前改动 | [验收矩阵](references/verification.md)：按影响范围验证并清理临时资源 |

已有画布先核实就绪记录；能力满足则跳过初始化细节，只在缺口处增量补齐。只初始化的请求以环境就绪为出口，不自动进入业务设计。

## 共同约束

优先复用项目画布、设计系统与实际组件；不限定技术栈。以实际入口和能力证据建模，区分现用、旧代码及新提议。交互预览必须隔离状态和副作用，不能用截图或重复静态 UI 代替。适用时使用可用的 aw-design-fake 和 aw-wording-reviewer，缺失时遵循工作流的降级边界。

画布认可不自动授权业务迁移；明确要求应用后尽量复用已审阅组件接入指定入口。完成本次范围内实现、评论修复与验收，报告未验证项，不默认在第一版停下等待批准。

下图概览初始化复用、设计闭环与迁移门槛，文本工作流为事实源。

![交互式流程画布设计工作流](docs/workflow.svg)
