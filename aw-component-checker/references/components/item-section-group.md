# Item Section Group

Gallery ID: `item-section-group`

## Definition & Semantics

Item Section Group 将相互关联的 Item 行组织为同一个内容分组，建立共享外框、背景和相邻关系。Small 与 Medium 分别为组内内容提供 12px 与 20px 横向内边距，并让未显式指定尺寸的 Item 继承同档行高；组件不附加纵向内边距、标题、选择模型或折叠状态。

## When to Use

当若干 Item 共享一个主题或设置范围，连续阅读比逐个独立卡片更清楚时使用。分组条件应来自内容关系，而不是凑齐固定数量。

## When Not to Use

无共同主题的行不应因排布相邻就归为一组。需要事件连续性或多属性比较时，不应用普通行分组掩盖其实际结构。

## Similar & Easily Misused Components

[Item](item.md) 表达单行意图，Item Section Group 表达多行之间的主题关系。[Item Surface](item-surface.md) 只为一个未分组 Item 提供独立表面。[Detail Activity Group](detail-activity-group.md) 表达事件连续性；[Detail Section Header](section-header.md) 为一个内容分区命名并可控制展开。

## Composition

### Recommended

将相关 Item 直接放在组内，并让组尺寸统一内容内缩和行高；分隔线与该尺寸的内容边缘对齐。需要分区名称时，在所属详情分区中与 Detail Section Header 配合。按 Detail Page Structure Scenario，成组触发条目可以作为详情分区的内容。

### Avoid

不要给每条 Item 再套一层 Item Section Group，造成每行都被暗示为独立分组；单项独立表面使用 Item Surface。不要增加额外纵向内边距，也不要因为组内包含多个 Checkbox 就把外层容器当成拥有全选逻辑的选择组。

## Internal Usage

本组件没有独立标签或值，内部判断主要是每个子行是否属于同一主题。组尺寸统一直接子 Item 的默认尺寸与横向内容边缘；行间分隔不代表流程先后，也不应被文案解释为步骤连接。

## Examples

### Recommended

界面主题和界面语言属于个人显示偏好，作为两个 Item 放在同一组中。

### Problematic

将账户删除、最近执行记录和帮助入口放在一组，仅因为三者都是横向排列的行。
