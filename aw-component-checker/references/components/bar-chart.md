# Bar Chart

Gallery ID: `bar-chart`

## Definition & Semantics

Bar Chart 用共同基线上的长度比较同一指标在不同类别或离散时间段的数量。图表主要回答哪些值较多、差异如何，不表示可选项或任务完成度。

## When to Use

各项数值具有同一单位和可比较口径，用户需要比较数量或排名时使用。当前实现是单组竖向柱形，适用于有限的离散类别。

## When Not to Use

不要在同一组柱中混用人数、金额与百分比。当前实现把负值的柱高截为零，因此包含负数的差异比较不能直接使用；该限制不代表所有柱形图都不能表达负数。

## Similar & Easily Misused Components

- [Pie Chart](pie-chart.md) 强调一个整体由哪些部分构成；Bar Chart 比较各项数值，不要求各项构成整体。
- [Table](table.md) 适合查阅精确值或同时比较多个属性；Bar Chart 适合概览单项指标的差异。
- [Progress](progress.md) 表示正在完成的任务，静态数量比较不能因柱形相似就当作进度。

## Composition

### Recommended

将图表与说明统计范围、单位和时间区间的标题关联。需要精确核对时提供同口径的 Table；筛选由外层 [Filter Bar](filter-bar.md) 管理，图表反映已生效范围。

### Avoid

不要把多个分别自动缩放的图表当作可直接按柱高跨图比较的结果。不要把柱子当作筛选或钻取按钮；当前组件没有专门的数据项选择契约。

## Internal Usage

类别标签、图例和 Tooltip 必须对应同一份数据，数值格式化不能改变单位或掩盖缺失值。零值与未取得的数据应明确区分；当前组件不会自动识别加载、错误与有效零值。

## Examples

### Recommended

用相同单位比较几个处理队列当天实际完成的记录数量，并提供对应精确数值。

### Problematic

把收入、支出后的负结余直接交给当前组件，负数柱变成零高，误导用户认为没有负值。
