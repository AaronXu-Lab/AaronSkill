# Segmented

Gallery ID：`segmented`。

## Definition & Semantics

Segmented 在少量、互斥的同级选项间切换一个持续保留的值，通常改变同一内容的视图模式或简单配置。当前组件保持一个有效选项被按下，重复点击不会清空选择。

## When to Use

当选项简短、可以同时理解，且切换结果能够直接映射到当前上下文时使用，例如同一数据的网格与列表。

## When Not to Use

不要把一组一次性命令做成 Segmented，也不要用 Segmented 表示允许多选或可以全部取消的集合。需要较长解释、大量选项或独立内容章节时，应重新选择结构。

## Similar & Easily Misused Components

- [Tabs](tabs.md) 组织有对应内容区域的同级章节；Segmented 更常改变同一内容的模式或参数，当前实现不创建 tabpanel。
- [Radio](radio.md) 适合需要逐项比较的答案，也可允许初始未选择。
- [Dropdown](dropdown.md) 收起值集合；Segmented 让少量取值持续可见。
- [Button](button.md) 执行一次动作，不天然保留当前选项。

## Composition

### Recommended

Segmented 可以与 Tabs、[Filter Bar](filter-bar.md) 同时出现，前提是三者分别控制章节、显示模式和筛选条件，且结果范围可解释。

### Avoid

不要在 Tabs 与 Segmented 中重复同一组选项，分别维护状态；这会产生两套并行导航。与 Switch 并排时，若二者实际控制同一个二值偏好，应保留语义更清楚的一种。

## Internal Usage

各选项 Label 应处于同一概念维度。图标选项必须有能识别模式的名称，不应依赖被隐藏的任意节点文本。当前值必须对应真实选项；默认首项不应被误解为用户已经作出业务确认。

## Examples

### Recommended

“活动记录”内容区域保持不变，Segmented 切换网格与列表，两种模式共享当前筛选条件。

### Problematic

Segmented 三项为“查看”“删除”“下载”，点击删除后该项持续高亮，一次性动作被误表示为当前模式。
