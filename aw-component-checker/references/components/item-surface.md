# Item Surface

Gallery ID: `item-surface`

## Definition & Semantics

Item Surface 为一个未分组 Item 建立独立外框、圆角和背景。Small 与 Medium 分别提供 12px 与 20px 横向内边距，并让未显式指定尺寸的 Item 继承同档行高；它不表达集合关系、排列规则或交互状态。

## When to Use

当一个 Item 需要独立于任何分组呈现，但仍需要清楚的表面边界时使用。适合单项能力摘要、轻量对象摘要或单个设置项。

## When Not to Use

多个相关 Item 应使用 Item Section Group 建立共享关系。仅需要裸行结构时直接使用 Item；需要网格、列表排列或完整对象卡片时，由对应布局或对象组件承担。

## Similar & Easily Misused Components

[Item](item.md) 负责单行信息结构，不提供表面。[Item Section Group](item-section-group.md) 负责多个相关 Item 的共享表面与分隔。[Grid Item](grid-item.md) 表达更完整的对象身份、摘要和对象操作，并可参与网格或列表布局。

## Composition

### Recommended

在 Item Surface 中直接放一个 Item，让 Surface 尺寸统一横向内容内缩与 Item 默认行高。外层页面或布局组件决定 Surface 之间的 Grid、List 和间距。

### Avoid

不要在 Item Surface 中堆叠多个 Item，不要让它负责同级 Surface 的排列。不要默认添加阴影、hover、点击或整行导航；需要交互时由明确的内部控件或更合适的交互组件承担。

## Internal Usage

外框、圆角、背景和横向内边距属于 Item Surface；标题、说明、Leading 与 Trailing 属于内部 Item。Surface 不增加纵向内边距，避免改变 Item 的四档约定行高。

## Examples

### Recommended

一个能力摘要以 Symbol、标题和单行说明组成，作为独立 Item 放在 Item Surface 中；外层网格决定它与其他能力项的排列。

### Problematic

把多个无关 Item 放进同一个 Item Surface，并通过阴影和整面点击暗示它是可导航卡片。
