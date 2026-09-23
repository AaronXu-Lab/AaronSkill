# Menu Item

Gallery ID：`menu-item`。

## Definition & Semantics

Menu Item 表达 [Menu](menu.md) 中一个可执行条目。条目可包含对象身份和辅助信息，但整行仍围绕一个菜单意图。当前 Menu.Item 是普通菜单项；真正的菜单内互斥选择由 Menu.RadioItem 管理。`hasNext` 表达条目会在当前 Menu 浮层内进入直接下级。

## When to Use

当某操作属于当前菜单的任务范围，需要用一条清楚的入口呈现时使用。对象条目也可以用于发起针对该对象的后续动作，例如进入权限确认。需要进入少量相关下级动作时使用 `hasNext`。

## When Not to Use

不要把普通菜单条目的尾部勾号当作已经实现了选择状态。静态信息段、复杂编辑表单或包含多个独立按钮的内容行，不应因为需要行样式就使用 Menu Item。

## Similar & Easily Misused Components

- [Item](item.md) 是一般信息行，可在内容区组织对象和辅助操作；Menu Item 依赖菜单上下文并执行一个菜单意图。
- [Action Button](action-button.md) 是宿主内直接可用的动作；Menu Item 是展开菜单后的条目。
- [Menu Header](menu-header.md) 是非交互分组标题。
- [Dropdown](dropdown.md) 提供字段值选择，不能把其中的选项等同于任意命令。

- [Sidebar Item](sidebar-item.md) 提供持久导航入口并表达当前位置；Menu Item 属于临时展开的菜单上下文，不能只因两者都是可点击行就互换。

## Composition

### Recommended

将 Menu Item 放入明确的 Menu 分组，必要时由条目打开 [Dialog](dialog.md) 完成后续输入或确认。条目涉及一个人或对象时，可用 [Avatar](avatar.md) 或 [Symbol](symbol.md) 辅助识别同一对象。

### Avoid

避免在整行菜单动作里嵌入另一个同级操作控件，使点击名称、图标和尾部时产生互相冲突的结果。`hasNext` 条目不得改用勾号、任意图标或文字作为尾部提示。需要同一组内互斥选择时，不要并行维护普通 Menu.Item 勾号和 Menu.RadioGroup 状态。

## Internal Usage

Label 表达动作或对象，description 解释同一条目的后果或身份。trailingText 只能提供相关辅助信息，快捷键提示必须真实有效。`hasNext` 固定覆盖尾部内容为向右 caret，并保持当前 Menu 打开以便同一浮层切换内容。默认尾部勾号只是呈现内容，不会赋予 aria-checked 或改变选择。破坏性语义只用于真实后果。

## Examples

### Recommended

“重命名”菜单项显示编辑图标，激活后进入当前对象的重命名 Dialog。

“更多设置”条目使用 `hasNext`，以固定向右 caret 说明它会进入 Menu 的直接下级。

### Problematic

三个普通 Menu.Item 都手工显示勾号来表示“当前视图”，但选择后旧勾号未清除，界面无法说明唯一当前值。
