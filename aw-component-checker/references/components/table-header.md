# Table Header

Gallery ID: `table-header`

## Definition & Semantics

Table Header 为表格列建立解释框架，并可在相应列提供排序或集合选择入口。当前 Panel 同时展示 TableHeader 的表头区域和 TableHead 的列头单元，排序能力属于 TableHead。

## When to Use

当正文单元格需要共同列名称，或用户能够对某列改变排序时使用。选择列可放置控制明确范围的全选控件，不能仅凭存在 Checkbox 就推定范围是全部数据。

## When Not to Use

不要用列头强调正文记录，也不要在没有排序结果更新的列上显示可排序入口。跨多列的页面标题不属于 Table Header。

## Similar & Easily Misused Components

[Table Cell](table-cell.md) 提供具体记录的值，Table Header 解释这些值。[Table Main Key](table-main-key.md) 识别某一行对象，不是列名称。[Detail Section Header](section-header.md) 组织一个内容分区，不为表格列定义属性。

## Composition

### Recommended

在 [Table](table.md) 的表头结构中为每个数据列提供对应列头。排序控件与调用方实际排序状态配对；表头 [Checkbox](checkbox.md) 与正文选择列及 [Bulk Action Bar](bulk-action-bar.md) 共享明确范围。

### Avoid

不要让点击排序同时触发筛选或导航。不要在同一个列头中放置两套含义相同但状态不同的排序控件；全选当前页时也不要让批量条宣称已选择全部匹配结果。

## Internal Usage

标签描述属性而不是某条示例值。排序图标表达当前顺序；全选名称说明被选择的对象或范围。选择列的 Checkbox 不应嵌入可排序按钮内部。

## Examples

### Recommended

“更新时间”列头触发按时间排序，图标随实际升序或降序更新；“选择当前页”控制该页可选记录。

### Problematic

表头显示降序图标，但点击后只翻转图标，没有改变记录顺序。
