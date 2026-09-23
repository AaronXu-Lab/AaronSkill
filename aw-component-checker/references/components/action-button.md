# Action Button

Gallery ID：`action-button`。

## Definition & Semantics

Action Button 表达依附于某个宿主组件或对象的局部操作。宿主提供操作对象和位置，按钮负责触发一个清楚的动作。当前组件可以显示文字、图标或图文；纯图标并不是定义条件。

## When to Use

当用户正在阅读一条记录、一段消息或一个字段，需要就地执行复制、编辑、展开菜单等辅助操作时使用。离开宿主后，按钮通常不再具有完整含义。

## When Not to Use

不要仅因为操作需要节省空间，就把页面的唯一提交入口降为 Action Button。只表示“已完成”而不能操作的图标，也不应使用按钮制造可点击预期。

## Similar & Easily Misused Components

- [Button](button.md) 可承担独立操作和流程主操作；Action Button 强调宿主内的局部辅助职责，区别不在有无文字。
- [Menu Item](menu-item.md) 是菜单中的操作条目；Action Button 可打开 [Menu](menu.md)，不承担菜单条目的结构职责。

## Composition

### Recommended

将 Action Button 放在 [Detail Field](detail-field.md)、[Message Footer](message-footer.md) 或条目明确提供的操作位。多个操作共享同一对象时形成一组；较次要的操作可由一个菜单触发器承接。

### Avoid

避免同时保留两组同等显著、执行同一对象同一动作的按钮。条目本身可点击时，不应让操作按钮的激活同时触发条目的导航。

## Internal Usage

名称、默认图标和 hoverIcon 必须表达同一个动作；悬停替换不能把“复制”变为“删除”。纯图标名称应说明动作，必要时带上目标对象。复制成功可以在原位置表达结果，但成功反馈不能继续暗示另一项可执行动作。

## Examples

### Recommended

详情字段显示记录编号，尾部 Action Button 复制该编号；成功后原位置显示复制反馈。

### Problematic

一个保存表单的唯一入口只显示在标题悬停时，且用无名称的圆点图标表示提交；流程主操作无法辨认。
