# Detail Hero

Gallery ID: `detail-hero`

## Definition & Semantics

Detail Hero 在详情内容顶部确立当前对象身份，集中表达名称、必要背景、对象级状态及主要操作。当前组件渲染顶层标题；对象身份已经充分明确时，Hero 可以省略。

## When to Use

当进入详情需要先确认正在查看哪个对象，以及对象的主要状态或行动时使用。对象级信息较丰富时，Hero 可为后续属性、历史和资源分区建立共同上下文。

## When Not to Use

主任务是编辑成组设置且标题已清楚标明上下文时，不要重复添加 Hero。集合中的每个小对象不应都使用详情顶层标题结构。

## Similar & Easily Misused Components

[Topbar](topbar.md) 提供页面身份、路径或页面操作；Detail Hero 提供内容内部的对象概览，二者可能互补，也可能重复。[Grid Item Infos](grid-item-infos.md) 是集合子项身份区。[Detail Field](detail-field.md) 表达一个属性，不承担对象总览。

## Composition

### Recommended

按 Detail Page Structure Scenario，对象级 [Alert](alert.md) 置于 Hero 之前，属性和活动放在后续内容分区。辅助 [Badge](badge.md) 表达对象状态，主要 [Button](button.md) 指向当前对象的核心行动。

### Avoid

不要让 Topbar 与 Hero 同时完整重复名称、描述和同一组操作。不要把只影响某个子分区的次要操作提升为 Hero 主操作，或将不同对象的状态混在同一身份区。

## Internal Usage

名称是对象身份，描述解释用途或背景；状态与主操作应适用于该对象整体。Symbol 只辅助识别。trailingContent 是组合内容槽，不会自动为业务操作赋予正确优先级。

## Examples

### Recommended

连接器详情显示连接器名称和用途，状态标明授权失效；上方 Alert 解释影响，重新授权成为清楚的恢复行动。

### Problematic

个人设置页已以“个人偏好”为标题，又增加同名 Hero、相同说明和重复保存按钮。
