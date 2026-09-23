# Table

Gallery ID: `table`

## Definition & Semantics

Table 将一组记录组织成具有共同列含义的行列结构，支持跨记录比较和按属性扫描。当前实现提供原生表格及其展示结构；数据获取、排序结果、筛选、选择集合和分页由调用方管理。

## When to Use

当多条记录具有可比较的共同属性，用户需要沿某列查找、排序或审阅差异时使用。表格内可以包含独立操作控件，是否可操作不改变行列对应关系。

## When Not to Use

不要用 Table 排版普通表单或不共享字段的说明块。需要电子表格式单元格编辑、区域选择或二维交互导航时，当前 Table 不能被当成已具备这些能力的工作表。

## Similar & Easily Misused Components

[Grid Item](grid-item.md) 以单个对象的身份与摘要为阅读单位；Table 以跨对象的列关系为单位。[Item](item.md) 适合一条信息及其控件，不要求各行字段对齐。[Table Header](table-header.md) 和 [Table Cell](table-cell.md) 是表格结构中的子职责，不能代替完整 Table。

## Composition

### Recommended

使用 Table Header 解释各列，使用 Table Cell 或 [Table Main Key](table-main-key.md) 表达记录。需要多选时，由同一选择集合连接 [Checkbox](checkbox.md) 与 [Bulk Action Bar](bulk-action-bar.md)；需要换页时，由调用方将 [Pagination](pagination.md) 连接到同一结果集。

### Avoid

不要让表头全选、行选择与批量操作分别维护互不一致的集合。不要把筛选后的页码和总数绑定到另一套未筛选数据，也不要把同一对象的导航与选择不加区分地绑定到整行点击。

## Internal Usage

同一列应保持同一属性、单位及操作含义。主标识用于识别记录，其他字段补充该记录；空值必须与零值、未加载或不适用区分。排序标记只能描述实际应用到该列的数据顺序。

## Examples

### Recommended

资源列表以名称、所有者和更新时间为列，用户比较所有者并按更新时间排序；行内菜单只作用于对应资源。

### Problematic

把“账号说明”“删除账号”和“最近通知”排进三行两列，只因为表格可以对齐内容；这些行没有共同字段关系。
