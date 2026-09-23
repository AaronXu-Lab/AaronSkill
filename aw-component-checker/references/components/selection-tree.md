# Selection Tree

Gallery ID: `selection-tree`

## Definition & Semantics

Selection Tree 组织具有父子关系的对象，并区分展开层级、选择目标与激活对象。当前支持浏览、单选和多选；可选分组在多选模式中代表包含当前及未来后代的动态范围，不等同于已加载后代的全选快照。

## When to Use

当父子关系影响用户寻找或选择对象，且需要按分支逐步展开时使用。允许选择分组之前，必须确认产品确实接受动态范围语义。

## When Not to Use

简单平铺选项不需要树。不要把逐项选中所有子项解释成自动选中父组；也不要把已选分组当作仅覆盖当前可见节点的静态集合。需要后者时应由产品另行建立明确模型。

## Similar & Easily Misused Components

[Dropdown](dropdown.md) 适合平铺的单值选择。[Sidebar Item](sidebar-item.md) 服务常驻导航或对象切换。[Checkbox](checkbox.md) 的集合全选常表达当前集合的聚合状态，而本组件的分组选择表达独立范围。[Selection Tree Item](selection-tree-item.md) 只是行呈现，树级行为由 Selection Tree 管理。

## Composition

### Recommended

按 File & Folder Picker Scenario，将树放入 [Dialog](dialog.md) 的选择任务中，由外层保留草稿并明确确认。浏览文件目录时可使用无选择模式；预览回调与提交选择继续保持不同职责。

### Avoid

不要另加一套与树不一致的 Checkbox 状态。避免把展开分支、选择分组和立即提交绑定成同一结果，让用户无法查看候选内容。选中分组后，不要允许后代独立取消却仍声称分组范围完整。

## Internal Usage

标签识别节点，图标解释节点类型，元信息补充同一对象。分组是否为空与分组是否可选是不同判断。当前多选取消显式选中的组会保留其可选直接子项为选择，其中子组仍为范围；调用方不能将该结果宣称为清空整组。

## Examples

### Recommended

选择一个持续同步的目录时，界面明确说明新加入的后代也包含在选择范围；展开目录只用于查看内容。

### Problematic

用户逐项选择了当前三个文件，界面把父目录自动显示为已选，并在后续加入文件时扩大选择。
