# Pie Chart

Gallery ID: `pie-chart`

## Definition & Semantics

Pie Chart 表达一个明确整体的组成，每个分段代表该整体中的一部分。图表的核心是部分与整体的关系，不是任意数值的并置。

## When to Use

数据项使用同一单位、彼此不重复，且能够共同解释一个整体时使用。用户主要需要判断组成或某部分占比，类别应能被清楚辨认。

## When Not to Use

不要把不同时间的同一指标、重叠成员集合或单位不同的数值拼成一个饼。当前实现只纳入正值并重新计算总量，负值、缺失数据和整体为零都不能当作普通构成结果处理。

## Similar & Easily Misused Components

- [Bar Chart](bar-chart.md) 适合比较各项数量与接近值，Pie Chart 适合表达整体构成。
- [Table](table.md) 适合精确查阅数值以及说明缺值或复杂分类，不能指望分段面积承担这些判断。
- [Progress](progress.md) 表示任务完成度；Pie Chart 的份额并不天然表示已完成与未完成。

## Composition

### Recommended

在图表附近说明整体的含义、统计范围与总量。使用图例或同口径 Table 解释类别；无有效数据时由 [Empty State](empty-state.md) 或相应反馈说明真实状态。

### Avoid

不要把来自不同总体的分段合并后仍称为同一整体。筛选后若总体发生变化，外层范围说明必须同步，不能保留原总量使用户误读占比。

## Internal Usage

分段、标签与 Tooltip 应使用同一个分类口径。当前 Tooltip 默认显示原始数值，并非自动百分比；百分比说明应与实际求和的总量一致。省略零值不能被解释为该类别不存在。

## Examples

### Recommended

统计同一批文件按互斥格式分类的占比，同时标明文件总数与统计范围。

### Problematic

将“我创建的文件”和“我收藏的文件”作为同一饼图的两部分，重复文件使整体含义失真。
