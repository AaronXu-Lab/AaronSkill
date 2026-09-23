# Detail Section Header

Gallery ID: `section-header`

## Definition & Semantics

Detail Section Header 为详情页的一段内容命名，并可控制该段内容的展开与收起。分区标题建立内容归属，折叠只改变可见性，不改变对象状态或选择；收起时 caret 持续可见，明确提示内容可以展开。

## When to Use

当详情内容可按明确主题分段，或某个较长分区需要渐进展开时使用。静态分区可只提供标题，折叠场景需要实际对应的内容和展开状态。

## When Not to Use

不要把分区标题当作进入另一页面的导航入口。没有所属内容时，不要显示一个暗示可展开的伪触发器；记录中的属性标签也不需要提升为分区头。

## Similar & Easily Misused Components

[Sidebar Section Header](sidebar-section-header.md) 组织侧栏入口；Detail Section Header 组织页面内容。[Table Header](table-header.md) 解释列属性。[Detail Field](detail-field.md) 解释一个值，不应自动产生分区层级。

## Composition

### Recommended

按 Detail Page Structure Scenario，将 [Detail Field](detail-field.md)、[Item Section Group](item-section-group.md) 或 [Detail Activity Group](detail-activity-group.md) 放入对应主题分区。空分区可由 [Empty State](empty-state.md) 解释缺少的内容。

### Avoid

不要由两个外层折叠控制器分别管理同一内容的显隐。标题旁的分区操作不应同时触发折叠；也不要在展开后才揭示与标题完全不符的另一个主题。

## Internal Usage

标题概括分区内容，数量说明计数范围，辅助操作限于当前分区。空状态与分区标题应描述同一类内容。当前组件的折叠需要 expanded 与 onExpandedChange 配合，不能把其中一个参数当作完整行为。

## Examples

### Recommended

“执行过程”分区展开后显示活动记录，旁边的数量表示该分区事件数。

### Problematic

“基本信息”的折叠箭头实际启动编辑弹窗，内容本身始终不受控制。
