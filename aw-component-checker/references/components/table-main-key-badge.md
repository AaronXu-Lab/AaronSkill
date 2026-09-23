# Table Main Key Badge

Gallery ID: `table-main-key-badge`

## Definition & Semantics

Table Main Key Badge 是行主标识旁的简短类别标记，用于补充“这条记录属于什么”。当前组件是展示性 span，没有内置选择、删除或菜单触发行为。

## When to Use

当名称不足以区分来源、类别或身份子类，而且该信息有助于理解主标识时使用。

## When Not to Use

不要用类别标记承载一段说明、可执行操作或多项过滤条件。需要独立状态语义及更完整的徽标能力时，应评估 Badge。

## Similar & Easily Misused Components

[Badge](badge.md) 是通用状态或类别标签；Table Main Key Badge 是依附表格主标识的类别补充。[Table Main Key](table-main-key.md) 承担对象识别与入口职责，不能由标记替代。

## Composition

### Recommended

放入 Table Main Key 的 badge 槽，与同一个对象名称共同阅读。仅在确实帮助识别时添加类别信息。

### Avoid

不要把重复类别标记同时放在名称旁和独立类别列中而没有额外阅读用途。不要将外观相似的标签与 [Filter Pill](filter-pill.md) 混排，使用户无法判断哪些可编辑筛选条件。

## Internal Usage

文字使用简短类别名，不能写成“删除”“查看”等操作指令。标记内容应补充名称，不复述名称本身。

## Examples

### Recommended

同名数据源来自不同系统时，在主名称旁标注来源类别。

### Problematic

把“删除文件”写在类别标记中，并依赖点击整个标记执行删除。
