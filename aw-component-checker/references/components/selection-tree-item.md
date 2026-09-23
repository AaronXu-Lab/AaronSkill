# Selection Tree Item

Gallery ID: `selection-tree-item`

## Definition & Semantics

Selection Tree Item 表达树中的一条轻量对象行，提供标签、前置信息和选择指示。当前单独组件没有完整树模型，不能自行管理层级、展开或选择集合。

## When to Use

在 Selection Tree 的行呈现或经过明确设计的树型组合中使用，且由父级提供节点关系和行为。Gallery 的独立行展示仅用于观察行状态，不代表可直接替代完整选择树。

## When Not to Use

不要只设置 selected 或显示 Checkbox，就声称已经实现多选树。平面设置行或常驻导航条目不需要借用树行。

## Similar & Easily Misused Components

[Selection Tree](selection-tree.md) 管理整体层级和选择模型。[Item](item.md) 组织一般信息与控件。[Sidebar Item](sidebar-item.md) 管理侧栏主操作及可折叠子项，职责与树候选行不同。

## Composition

### Recommended

优先让 Selection Tree 根据节点数据产生行。在自定义组合中，父级应统一提供选中状态、展开操作和节点激活逻辑，尾部指示与父级同源。

### Avoid

不要在树行和尾部 Checkbox 中分别保存不同选择状态。前置展开按钮若存在，不应因事件传播再次执行行选择或相反操作。

## Internal Usage

标签与图标描述同一节点；checkmark 或 Checkbox 表达该节点在当前模型中的选择。spinner 表达后代尚未就绪，不能同时被解释为选中标志；单独行的 disabled 展示不替代调用方的行为约束。

## Examples

### Recommended

完整 Selection Tree 在多选模式下为节点生成尾部 Checkbox，节点状态随树的统一 value 更新。

### Problematic

多个独立 Selection Tree Item 只切换自己的勾号，没有父子关系或整体选择结果，却被用作目录授权选择器。
