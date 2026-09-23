# Filter Bar

Gallery ID：`filter-bar`。

## Definition & Semantics

Filter Bar 构建和编辑作用于当前数据集合的一组筛选条件。组件负责添加维度、选择值、修改和移除条件；筛选改变可见结果范围，不直接改变对象本身。

## When to Use

当用户需要按一个或多个预定义维度逐步收敛结果，并且已生效条件应持续可见时使用。当前 single 限定一个维度，multiply 允许多个维度，每个维度保留一个已选值。

## When Not to Use

不要把批量修改对象属性、切换业务模块或一次性执行查询命令混作筛选条件。复杂的范围表达式、同维度多值和自由逻辑组合，不能由当前简单 key/value 模型自动推出。

## Similar & Easily Misused Components

- [Filter Pill](filter-pill.md) 表示一个条件并提供操作目标；Filter Bar 管理条件集合和添加流程。
- [Dropdown](dropdown.md) 选择单个字段值；Filter Bar 还需要表达哪些维度正在限制结果。
- [Segmented](segmented.md) 切换少量模式或简单范围，Filter Bar 适合可添加与移除的条件集合。
- [Bulk Action Bar](bulk-action-bar.md) 操作已选对象，不决定列表筛选范围。
- [Content Group](content-group.md) 仅收拢展示已有标签，不管理筛选条件；外观相似的标签集合不等于 Filter Bar。

## Composition

### Recommended

将 Filter Bar 放在其控制的 [Table](table.md) 或列表附近。与 [Tabs](tabs.md) 并用时明确章节范围，与 Segmented 并用时明确展示模式；三者可以互补。

### Avoid

不要在另一个表单或 Dropdown 中重复保存同一条件却不与 Filter Bar 同步。筛选结果为空时，不能隐藏所有条件入口，让用户无法恢复范围。

## Internal Usage

每个条件需要明确的维度名称和可理解的值名称。当前内部未完成选值的 pending 条件不会作为已提交值交给调用方；界面不能把“已选维度”误称为“筛选已生效”。条件 key 和值应对应可用定义，组件不替调用方解释业务运算。

## Examples

### Recommended

记录列表显示“状态：失败”和“负责人：我”，用户移除负责人条件后，结果范围随之扩大。

### Problematic

“状态：失败”筛选胶囊被移除后，列表仍保留隐形失败条件，用户无法理解结果范围。
