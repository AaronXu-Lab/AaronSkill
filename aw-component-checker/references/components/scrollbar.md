# Scrollbar

Gallery ID: `scrollbar`

## Definition & Semantics

Scrollbar 控制所属内容区域的可见位置，帮助用户访问已经属于该区域但位于视口之外的内容。滚动位置不是任务进度、数据选择或分页编号。

## When to Use

一个明确的内容区域确实存在溢出，且采用 Base UI ScrollArea 组合管理该区域时使用。Scrollbar 必须对应实际发生滚动的 viewport。

## When Not to Use

不要把 Scrollbar 当成任意数值滑块，也不要只为了界面装饰放置没有对应溢出的轨道。切换服务器数据页应由分页职责承担。

## Similar & Easily Misused Components

- [Pagination](pagination.md) 切换同一集合的数据页；Scrollbar 改变当前内容区域的可见位置，不能推断为已经加载下一页。
- [Progress](progress.md) 表达任务程度，Scrollbar 表达位置。
- [Turn Navigator](turn-navigator.md) 跳转到明确的会话轮次，Scrollbar 不提供内容索引。

## Composition

### Recommended

在 Base UI 的 Root、Viewport、Content 结构中使用 Scrollbar，让拖动与原生滚动共享一个位置。[Table](table.md) 已提供内置横向滚动配置时，直接使用该配置。

### Avoid

不要在同一方向为同一内容建立两个独立 viewport 和两条竞争的滚动条。嵌套滚动仅在内容区域具有独立边界时成立，不能让外层和内层共同模拟同一条连续内容。

## Internal Usage

当前 Scrollbar 内部管理 Thumb，方向应与所属 viewport 的溢出方向一致。组件不接受任意受控进度值，也不能直接绑定另一个外部滚动区域；位置与范围来自所属 ScrollArea。

## Examples

### Recommended

对象选择弹窗保留标题与确认区，候选内容在唯一的 ScrollArea 内滚动。

### Problematic

表格启用内置横向滚动后，调用方又套一层独立横向滚动容器，两个位置彼此不同步。
