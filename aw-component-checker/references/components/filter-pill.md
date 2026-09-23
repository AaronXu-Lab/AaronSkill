# Filter Pill

Gallery ID：`filter-pill`。

## Definition & Semantics

Filter Pill 表达一个筛选维度及其当前值，是已应用条件的紧凑操作入口。当前组件可提供一个整体选择目标，或把修改值与移除条件分为两个目标；组件自身不执行筛选。

## When to Use

当用户需要直接识别、编辑或移除某个筛选条件时使用。宿主提供条件含义和当前值，并负责让数据结果与条件保持一致。

## When Not to Use

不要用 Filter Pill 表示对象的只读分类或运行状态，也不要把移除筛选条件解释成删除对象。当前组件不是自由多选标签编辑器。

## Similar & Easily Misused Components

- [Filter Bar](filter-bar.md) 管理条件集合及添加流程；Filter Pill 是单个条件的入口。
- [Badge](badge.md) 描述对象状态或分类；Filter Pill 让用户控制结果范围。
- [Dropdown](dropdown.md) 是完整的值选择控件；Filter Pill 的选择目标需要宿主连接实际编辑内容。

## Composition

### Recommended

在 Filter Bar 中由父级管理条件集合，或与 [Menu](menu.md) 的单选条目组合编辑当前值。移除入口独立作用于该条件，结果区域保留在同一工作上下文。

### Avoid

避免给同一胶囊再套一个整行点击处理，使移除同时打开编辑菜单。不要用一个共同的关闭按钮同时清除多个未明确归组的条件。

## Internal Usage

文字应表达维度与值，或在维度已明确时表达无歧义的值。移除名称应指向被移除条件。当前 disabled 等按钮属性只透传到主目标，独立移除目标由 onRemove 管理；不能推定禁用主目标就冻结整颗条件。

## Examples

### Recommended

“负责人：我”的主目标打开负责人选择，尾部移除按钮仅取消该筛选条件。

### Problematic

对象旁的“已发布”Filter Pill 实际只是只读状态，点击后没有筛选行为；交互外观误导了用户。
