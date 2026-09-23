# Detail Activity Group

Gallery ID: `detail-activity-group`

## Definition & Semantics

Detail Activity Group 将若干 Detail Activity 组织为同一对象的活动历史，并可表达相邻事件的连续性。组件不计算排序、时间或业务因果关系。

## When to Use

当一组事件属于同一对象或清楚命名的历史范围，且顺序对理解过程有价值时使用。调用方需要先确定时间方向和事件边界。

## When Not to Use

无共同历史范围的消息、静态属性或设置项不应放入活动组。连接线不能替代真实的事件先后，也不能凭空表示执行依赖。

## Similar & Easily Misused Components

[Detail Activity](detail-activity.md) 表达单个事件，Group 表达事件之间的连续阅读关系。[Item Section Group](item-section-group.md) 只组织主题相近的普通行。[Table](table.md) 更适合跨事件比较多列属性。

## Composition

### Recommended

将同一历史范围的 Detail Activity 放在由 [Detail Section Header](section-header.md) 命名的分区中。按 Detail Page Structure Scenario，活动组与对象身份、属性分区属于不同内容职责。

### Avoid

不要把多个对象无标识地交错成一条事件链。避免将筛选或分页前后的片段连接成看似完整的历史，却不说明当前范围。

## Internal Usage

本组件没有独立标题或时间字段，需检查子事件是否属于同一范围、顺序是否一致。showLine 只控制连接呈现，不能被解释为组件已经推导事件关系。

## Examples

### Recommended

任务详情在“最近运行”下按同一时间方向展示三次运行记录，每行说明对应时间与结果。

### Problematic

把“创建者”“运行成功”“启用开关”连续连接，混合了属性、事件和控制项。
