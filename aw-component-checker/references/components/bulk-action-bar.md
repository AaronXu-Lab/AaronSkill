# Bulk Action Bar

Gallery ID: `bulk-action-bar`

## Definition & Semantics

Bulk Action Bar 为当前选择集合提供批量操作，明确操作将作用于哪些已选对象以及如何退出选择。组件接收选择数量与回调，不保存选择集合，也不自动在数量为零时隐藏。

## When to Use

当用户已选中一个或多个对象，且同一操作能够合理作用于该集合时使用。调用方应明确跨页选择、不可操作对象和清空选择的规则。

## When Not to Use

没有选择集合的页面级操作不需要批量条。不能用只读总条数冒充已选数量，也不应把“取消选择”解释为撤销已经完成的批量操作。

## Similar & Easily Misused Components

[Menu](menu.md) 为上下文提供操作集合；Bulk Action Bar 额外明确多选范围和退出路径。[Button](button.md) 触发单个操作，不能单独表达整个选择上下文。[Tabs](tabs.md) 组织视图，批量条可在明确进入选择模式时替换其位置，但不接管视图状态。

[Filter Bar](filter-bar.md) 改变结果范围；Bulk Action Bar 作用于明确的已选集合，筛选结果不能自动等同于批量操作目标。

## Composition

### Recommended

与 [Table](table.md) 或 [Grid Item](grid-item.md) 的统一选择模型连接。少量操作直接展示，空间不足由组件收起到 Menu。操作需要确认时，由调用方组合 [Dialog](dialog.md)，并保持确认目标仍是该选择集合。

### Avoid

不要让数量显示当前页选择数，实际操作却作用于全部结果。进入批量模式后，若行内操作会造成单项与集合目标混淆，应暂时隐藏、禁用或清楚区分；不必一概禁止所有行操作。

## Internal Usage

计数描述已选对象，取消只清除选择。每个操作的名称与回调应一致；混合权限或状态时，调用方决定可用性并解释范围。当前操作仅在传入对应回调后出现，改标签不会新增能力。

## Examples

### Recommended

用户选中三个文件，批量条显示“已选择 3 项”；归档确认仍明确指向这三个文件，取消选择则恢复普通列表操作。

### Problematic

批量条显示“已选择 3 项”，删除回调读取了当前全部搜索结果，实际删除 40 个对象。
