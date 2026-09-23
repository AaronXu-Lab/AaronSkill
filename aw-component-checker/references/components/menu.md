# Menu

Gallery ID：`menu`。

## Definition & Semantics

Menu 是与触发器或当前对象相关的临时操作集合。Menu 组织菜单条目及分组；动作条目执行操作，菜单内的互斥选项由相应选择结构表达，不能只靠勾号区分。`isNext` 可把同一浮层切换到一个直接下级，且由固定返回条目回到上级。

## When to Use

当一个对象或当前位置有若干相关动作，直接展开全部动作会干扰主要内容时使用。轻量上下文配置也可以进入菜单，但用户必须能理解选择范围和生效结果。一个条目需要展开少量、单层的相关动作时，可以在同一 Menu 中进入下级。

## When Not to Use

不要把长期阅读内容、复杂表单或持续工作区装进 Menu。自由输入并筛选候选值的交互需要完整的候选输入契约，不能因当前浮层样式相似，就把任意 Input 加 Menu 视为现成的搜索选择组件。不要用连续多层 Menu 代替需要位置感、历史或复杂导航的界面。

## Similar & Easily Misused Components

- [Dropdown](dropdown.md) 以字段当前值为核心，Menu 以当前上下文可做什么为核心。
- [Tooltip](tooltip.md) 提供非交互补充说明；Menu 提供可执行条目。
- [Dialog](dialog.md) 承载需集中处理的明确任务；Menu 可以触发任务，但不代替任务正文。
- [Menu Item](menu-item.md) 与 [Menu Header](menu-header.md) 分别承担单项和分组标题。

## Composition

### Recommended

用 [Button](button.md) 或 [Action Button](action-button.md) 作为触发器，由 Menu 管理浮层，相关条目按任务分组。菜单内单选使用当前 Menu.RadioGroup 与 Menu.RadioItem；需要继续填写信息的动作可打开 Dialog。进入下级的条目使用 Menu Item 的 `hasNext`，下级浮层设置 `isNext` 并由 `onBack` 返回上级。

### Avoid

不要为同一动作同时设置普通条目、嵌套按钮和另一个独立触发器。不要为下级入口另配不同的尾部图标，也不要在下级内容中自行复制返回条目或返回条目后的 Divider。一般分隔线只出现在两个非空分组之间；下级 Menu 固定用 Divider 区分返回操作与下级内容。资源分享 Scenario 的输入搜索结果由调用方控制过滤、焦点和后续邀请任务，属于专门组合，不能据此省略其他搜索选择场景的设计判断。

## Internal Usage

Composer 的 @ 建议可使用 `Menu.Popup anchor` 连接光标虚拟锚点，使用 `focusTarget` 将焦点保持在编辑器。此组合需 Root modal=false、highlightItemOnHover=false，并忽略 focus-out 关闭请求；外部点击仍关闭。调用方通过编辑器建议键盘回调管理高亮与确认，并用 suggestionMenuId/suggestionActiveDescendant 关联菜单条目。外部焦点组合进入下级后，调用方把内置返回项加入同一 action 列表，通过 `backItemId` 让 aria-activedescendant 指向真实返回项，通过 `backItemHighlighted` 同步当前高亮，Enter 继续调用 `onBack`；不能复制返回条目。普通菜单不传 focusTarget 与这两个返回项控制属性，继续使用 Menu 默认焦点导航和高亮。

触发器名称说明操作对象或动作集合。分组标题说明条目的共同用途；条目名称应让用户预判执行结果。`isNext=true` 时，Menu 固定在内容前增加带返回图标的条目及其下方 Divider；调用方可通过 `backLabel` 提供本地化返回文案，未提供或传入空字符串时返回条目只显示图标。点击返回条目或按 Escape 都返回上级，并使用相同的层级过渡。回到上级后，Escape 恢复 Menu 默认的直接关闭行为。层级切换由同一浮层承接，浮层高度在新旧自然尺寸间过渡并裁切移动中的内容，旧内容向左淡出，新内容从右侧向左淡入。选中标记、快捷键或辅助说明必须指向当前条目，不能制造未实现的行为。

## Examples

### Recommended

一条文件记录的“更多操作”菜单提供重命名和复制链接，重命名再打开单一任务 Dialog。

“移动到”条目使用向右 caret 进入一个简短位置列表；调用方传入 `backLabel="Back"` 后，下级顶部提供 Back；传入 `backLabel=""` 时只显示返回图标。两种状态都用 Divider 与位置列表区分。若该 Menu 把焦点保留在外部编辑器，返回项通过 `backItemId` 与 `backItemHighlighted` 纳入同一套上下键、Enter 和 aria-activedescendant 管理。

### Problematic

菜单展开后是带保存按钮的长篇设置表单，用户离开触发器就失去正在进行的工作区。
