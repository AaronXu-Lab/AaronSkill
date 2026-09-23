# Figma 组件治理工作流

本文档是执行 AW Figma Component Governance 时优先读取的文本工作流，也是 `workflow.svg` 的语义事实源。SVG 是与本文档同步的可视化投影。

## 输入与产物

- 输入：待治理的 Figma Component 或 Component Set，以及用户明确的治理范围。
- 产物：经过窄范围治理与回读验证的组件、固定格式的人工值排序说明和结构化 JSON 审计。

## 执行步骤

1. 读取组件集名称、属性、Variant、直接子层、内部层、尺寸和 `componentPropertyDefinitions`。
2. 判断每个变化应使用 Variant、Boolean Property、Instance Swap Property 还是 Slot，避免 Variant 爆炸。
3. 按语义命名、属性优先级和值顺序规划变更；保留未要求重设的视觉样式和外部实例内部结构。
4. 加载必要字体，使用稳定 node ID 做小步写入，每次关键写入后立即回读。
5. 对比每个 `variantOptions` 的当前与目标顺序。
   - API 可安全完成的名称排序：执行并验证。
   - 现有值顺序无法安全修改：保留组件身份，转为人工拖动说明。
6. 输出固定的 `Manual Value Reordering` 章节；没有缺口时也使用规定的无操作文本。
7. 生成 `component-governance-audit.json`，确保重命名、建模决策、排序缺口、验证结果和风险与 Markdown 一致。

## 停止条件

- 目标组件或 Component Set 身份不明确时停止确认。
- 变更需要重建组件集、破坏发布身份或影响实例，且用户未明确接受风险时停止。
- 字体未加载或回读结果与写入预期不一致时，不继续批量写入。
- 公共 Plugin API 无法安全重排值时，不用重建规避，转为人工操作。

## 最终交付

交付治理结果、固定人工排序章节和结构化审计文件，并列出所有未解决的人工操作与风险。
