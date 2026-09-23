# Menu Header

Gallery ID：`menu-header`。

## Definition & Semantics

Menu Header 为一组相关菜单条目提供非交互标题。标题帮助理解分组，不执行操作，也不表示当前选择。正式 Panel 对应展示型 MenuHeader，以及 Menu.GroupLabel 提供的组名称组合。

## When to Use

当菜单中有多个需要解释的条目分组，或一组菜单单选需要明确选择维度时使用。组名称应提供条目自身无法清楚表达的范围信息。

## When Not to Use

不要把 Menu Header 用作禁用的菜单操作，也不要用标题位置放置独立“管理”按钮。只有一个简单分组且含义已清楚时，不必重复增加相同标题。

## Similar & Easily Misused Components

- [Menu Item](menu-item.md) 是可执行或可选择的条目；Menu Header 只是说明组的含义。
- [Menu](menu.md) 管理浮层与分组结构；Menu Header 没有独立浮层或导航职责。
- [Detail Section Header](section-header.md) 可以组织页面章节并支持折叠，不能仅因标题外观类似就替代菜单组标题。

## Composition

### Recommended

在 Menu.Group 中使用 Menu.GroupLabel，让结构与名称对应。Dropdown 的选项分组也可复用 Menu Header 的展示，但选择关系继续由 Dropdown 的原语负责。

### Avoid

避免标题后没有条目、条件分组消失后残留标题，或在单个条目之间重复相同标题。不能用点击标题同时“选择整组”却保留非交互标题语义。

## Internal Usage

标题文字应概括组内条目的共同维度，不能写成与条目平级的命令。当前 MenuHeader 是展示型 div；在菜单中需要正式分组命名时，应使用 Menu.GroupLabel 的组合。

## Examples

### Recommended

“按来源筛选”标题下列出菜单内互斥来源选项，标题说明所有选项共享的问题。

### Problematic

“删除全部”放在 Menu Header 中并绑定点击事件，外观与结构宣称标题，行为却是危险操作。
