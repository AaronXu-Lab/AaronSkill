# Session End

Gallery ID: `session-end` · 家族：Session

## Definition & Semantics

Session End 表示当前会话无法继续输入的边界，并可说明原因及提供后续入口。组件代替不可用的 Composer；名称不意味着会话数据必须被删除或执行任务必须已经完成。

## When to Use

用户仍可查看会话，但因权限、生命周期或其他明确条件不能在当前会话继续输入时使用。调用方应知道阻止继续的实际原因。

## When Not to Use

不要把暂时加载、某次操作失败或一条回答完成当作整个会话截止。只读状态可以构成输入边界，但应明确说明只读原因，不能笼统宣称任务成功。

## Similar & Easily Misused Components

- [Composer](composer.md) 提供继续输入入口，Session End 说明该入口当前不可用。
- [Alert](alert.md) 通知问题或风险，未必阻止继续会话。
- [Empty State](empty-state.md) 表示内容区域没有对象；Session End 可以出现在拥有完整历史记录的会话中。

## Composition

### Recommended

保留已有消息供用户阅读，在原输入区域显示边界原因；确有下一条路径时提供一个含义明确的行内操作，例如创建可编辑副本。

### Avoid

不要在 Session End 下方继续保留正常可用的发送入口，形成“已结束”和“仍可继续”的冲突。也不要同时显示重复的全页空态，遮挡仍有效的会话历史。

## Internal Usage

说明文字回答为何不能继续，图标辅助表达该原因，操作文字说明将打开或创建什么。组件不会推导权限或自动创建新会话；展示恢复操作时必须连接实际处理，不应让普通关闭被理解为恢复权限。

## Examples

### Recommended

用户查看共享的只读会话，输入位置说明无法编辑，并提供“创建副本”。

### Problematic

助手完成一次回答后显示“会话已结束”，但用户实际仍可发送下一条请求，状态与可用能力矛盾。
