---
name: aw-design-system-gallery
description: 创建或修改设计系统 Gallery 展示时使用，包括新增或修改组件时顺带创建或调整 Gallery Panel、默认或对比示例、属性轴、Caption、占位文案或图标，即使用户未明确要求 Gallery 审查；不用于完全不涉及 Gallery 的普通组件实现或产品文案修改。
metadata:
  version: "3.18.1"
  author: "aaron_xu"
  creation_context: "为以可控成本优化设计系统组件的 Gallery 展示，使属性轴、示例结构与目标项目事实源保持一致，并支持从局部改进渐进扩展到获授权的批量审查而创建。"
---

# AW Design System Gallery

以目标项目的事实源和 Gallery 约定审查或优化组件展示。执行模式、授权范围、证据与完成标准见 [Gallery 工作流](docs/workflow.md)；首次执行读取这份短工作流，本会话已读且仍适用时直接复用。

## 按任务读取

下表指向详细规则的唯一维护位置。按本次实际动作读取对应章节，不因文件存在而通读；任务跨多项时组合读取，完整 Gallery 审计覆盖全部适用章节。只改现有轴的顺序无需重新筛选所有场景；新增场景、增删展示轴或改变 Caption 表达的属性或状态时同时读取正式展示筛选。

| 当前任务 | 读取资料 |
| --- | --- |
| 选择展示轴、筛选正式场景、调整 Caption | [§2 正式展示筛选](references/gallery-rules.md#2-选择设计审阅轴) |
| 排列依赖轴、核对 default、处理无轴组件 | [§3 轴顺序与默认示例](references/gallery-rules.md#3-决定轴顺序) |
| 核对名称映射、组件契约或修改 API | [§4 名称与 API](references/gallery-rules.md#4-核对-gallery-名称与实现-api)，按其链接读取相关 API 约束 |
| 判断、增改真实占位范围提示或接入边界开关 | [§5 范围提示](references/gallery-rules.md#5-决定真实占位范围提示) |
| 调整示例内容、比较布局或浮层表面 | [§6 可比较示例](references/gallery-rules.md#6-构造可比较示例) |
| 审阅复合组件、父级组合或子级矩阵 | [§7 父子展示](references/gallery-rules.md#7-展示复合组件与公开子组件)；涉及轴选择时同时读 §2 |
| 调整通用分类或迁移 Panel | [§8 分类与稳定标识](references/gallery-rules.md#8-组织通用-gallery-分类) |
| 验证实施结果 | 对应规则的验收条件与 [§9 验证与恢复](references/gallery-rules.md#9-验证与恢复) |

## 工作流概览

![Gallery 工作流程](docs/workflow.svg)
