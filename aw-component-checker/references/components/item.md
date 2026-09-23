# Item

Gallery ID: `item`

## Definition & Semantics

Item 以 Leading、标题／单行说明和 Trailing 组织一个信息或设置意图。它是无外框、无横向内边距的行结构，不预设整行导航或选择；真正的操作、选择和状态控制由内部控件承担。

## When to Use

当一条内容可以由标题与可选单行说明表达，并由可选身份标识、紧凑标题标记、一个值或一个控制意图补充时使用。Small 与 Medium 只改变约定行高；Leading 和 Trailing 的内容不能改变行高。

## When Not to Use

不要把多个互不相关的设置塞进同一行。需要多属性横向比较、完整对象摘要卡片或独立导航项时，应选择对应结构；不能因外观像列表就把 Item 当作菜单项。

## Similar & Easily Misused Components

[Detail Field](detail-field.md) 重点是属性标签与值，Item 重点是一条信息及其控制意图。[Table](table.md) 用共同列组织多条记录，Item 不提供跨行属性比较结构。[Grid Item](grid-item.md) 以完整对象身份和摘要为中心。[Menu Item](menu-item.md) 在上下文菜单中执行选择或操作；[Sidebar Item](sidebar-item.md) 负责常驻侧栏导航。[Item Section Group](item-section-group.md) 为多个相关 Item 建立共享边界，[Item Surface](item-surface.md) 只为一个未分组 Item 建立独立边界。

## Composition

### Recommended

同类行用 [Item Section Group](item-section-group.md) 建立分组，单个未分组行用 [Item Surface](item-surface.md) 建立独立表面。按实际意图组合 [Button](button.md)、[Dropdown](dropdown.md)、[Switch](switch.md)、[Checkbox](checkbox.md)、[Radio](radio.md) 或 [Segmented](segmented.md)，由调用方提供真实状态和回调。

### Avoid

不要在 Item 自身补外框、横向内边距、阴影或 hover 表面；这些属于外层组合。不要让整行点击与内部控件执行不相干的操作，也不要堆叠多个独立操作；低频多操作应由一个 Menu 入口收纳。多个 Radio 若表达互斥选择，必须共享一个选择模型，而非各自独立。

## Internal Usage

Leading、标题、说明、标题旁 Badge 与 Trailing 必须属于同一个信息对象或设置对象。说明只补充适用条件并保持单行省略；标题 Badge 是紧凑附属信息，不能取代或挤占独立的 Trailing。尾部一次承载一个值、状态或控制意图。当前实现的默认 Text 内容和默认控件仅提供通用回退，正式场景应传入有意义的内容和行为。

## Examples

### Recommended

“自动保存”行说明保存时机，尾部 Switch 控制该功能当前是否开启。

### Problematic

“通知”行同时放邮箱输入、删除账号和语言选择；这些内容无法归于一个清楚的设置意图。
