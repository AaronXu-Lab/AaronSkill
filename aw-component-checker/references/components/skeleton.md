# Skeleton

Gallery ID: `skeleton`

## Definition & Semantics

Skeleton 预告尚未就绪的内容结构，告诉用户这里将出现内容。占位形状不是实际对象，也不代表已加载的空值。

## When to Use

结果内容尚未返回，但字段、列表或摘要的基本结构已知时使用。可按独立内容区域结束占位，不必等待所有无关请求同时完成。

## When Not to Use

不要在结构未知时编造固定记录，也不要把 Skeleton 当作匿名化、禁用或失败状态。已经可以使用的固定操作不应因为附近数据加载而被替换成虚假控件。

## Similar & Easily Misused Components

- [Spinner](spinner.md) 表示一个操作仍在进行；Skeleton 表示预计出现的内容。
- [Progress](progress.md) 表示任务完成程度，Skeleton 不承诺比例或剩余时间。
- [Empty State](empty-state.md) 表示确认没有内容；Skeleton 表示尚不知道结果。

## Composition

### Recommended

在已知结构的 [Table Cell](table-cell.md) 或详情内容范围中使用 Skeleton，保留当前已有依据的表头和任务入口。仅替换尚未可用的内容，避免将旧的有效数据误标为不存在。

### Avoid

不要让同一字段同时显示 Skeleton 与 Empty State。不要将整个 Dialog 的标题和关闭入口都变成骨架，模态任务的边界仍需要可识别。

## Internal Usage

每个占位应对应真实内容角色；不要在占位中嵌入可点击按钮、实际业务数值或表示完成的图标。组件只提供占位呈现，结束加载与失败转换由调用方决定。

## Examples

### Recommended

文件列表保留列标题，在尚未加载的名称与更新时间单元格中展示占位。

### Problematic

读取失败后骨架一直保留，界面没有说明失败，也没有可以继续处理的入口。
