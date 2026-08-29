# 设计 Token 一致性审计工作流

本文档是执行 AW Design Token Consistency Auditor 时优先读取的文本工作流，也是 `workflow.svg` 的语义事实源。SVG 是与本文档同步的可视化投影。

## 输入与产物

- 输入：Figma Variables、`DESIGN.md`、CSS/Less 三类来源中的任意两类或三类。
- 产物：同一轮审计生成的 `token-audit.json`、`token-audit.csv` 和 `token-audit.md`。

## 执行步骤

1. 确认两个或三个不同来源及其路径或 URL；用户路径优先于脚本默认路径。
2. Figma 来源只导出指定 Token collection 的紧凑变量数据，并排除 `Other` collection。
3. 读取 Token 归一化、平台值映射和输出 schema，再运行内置审计脚本。
4. 保留原始名称和值，只对比较副本做规范化；解析 CSS alias，并排除非事实源变量的覆盖计数。
5. 按固定 issue 类型区分缺失来源、缺失 Token、单源 Token、值不匹配、规范名冲突和未解析引用。
6. 用输出 schema 校验三份产物，确认所选来源、来源状态、计数和 issue 数组彼此一致。
7. 以中文优先的摘要交付三份报告，并按缺失来源、值差异、缺失 Token、单源判断、映射改进的顺序解释。

## 停止条件

- 少于两个有效且不同的来源时停止并索取缺失输入。
- 来源不可读时记录 `missing_source`，不得把两源结果冒充三源审计。
- 映射的语义等价性无法确认时保留为显式问题，不按值相等自动合并。
- 任一产物不符合 schema 或三份产物不一致时不得交付完成结果。

## 最终交付

交付 Markdown、JSON、CSV 三份审计文件及关键计数。只提供修复证据和输入，不自动删除或改写来源 Token。
