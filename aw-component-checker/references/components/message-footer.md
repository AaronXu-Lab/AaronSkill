# Message Footer

Gallery ID: `message-footer` · 家族：Message

## Definition & Semantics

Message Footer 是单条消息的附属信息与操作区域。当前有时间加操作、纯文字两种内容语义；纯文字适合消息状态，操作组针对所属消息执行复制或调用方提供的行为。次要的局部命令可收纳到可选的溢出 Menu，不增加第二组平铺操作。

## When to Use

消息需要显示时间、次要状态或局部操作时使用。页脚信息应帮助理解或处理该条消息，而非承载主消息内容。

## When Not to Use

不要把全会话设置、任务启动或输入发送放入没有对应消息对象的 Footer。需要用户立即阅读的重要结论也不应只放在附属页脚中。

## Similar & Easily Misused Components

- [Message Query](message-query.md) 与 [Message Answer](message-answer.md) 提供消息边界，并负责页脚的位置、对齐与显示时机。
- [Action Button](action-button.md) 执行页脚中的局部操作；Footer 组织这些操作与消息元信息。
- [Message Activity](message-activity.md) 展示过程与详情，Footer 适合紧凑状态或操作。

## Composition

### Recommended

将 Footer 放入所属消息的 footer 插槽；需要状态与操作切换时，通过 activeFooter 指定另一层。

### Avoid

不要在消息外再建一套并行的复制或编辑工具栏。

## Internal Usage

扩展默认复制时可使用 actions 函数保留内置复制反馈，并加入同一消息的操作。次要命令通过 `menuActions` 进入省略号 Action Button 的 Menu；每项必须提供真实的 label、可选 icon 与处理逻辑，Menu 仅在有项时出现。静态状态不能因为复用了按钮而变成无响应的操作；纯状态优先使用 text 内容类型。

时间、复制内容与所有回调必须指向同一条消息。只有具备有效编辑处理时才提供 Edit；组件不推断最后一条、排队或可编辑资格。actions 数组替换整组默认操作，不能误以为会自动追加。text 类型只显示 text，不应期待同时保留时间和操作。复制成功反馈应表示实际复制成功。

## Examples

### Recommended

待发送消息常显“排队中”，激活后显示复制、编辑与取消；各回调均携带该消息身份。

一条 Answer 的次要“查看运行详情”命令在溢出菜单中以 Eye 图标与文案出现；菜单触发器与该命令都只处理这条 Answer。

### Problematic

页脚显示“复制回答”，实际复制的是上一条用户输入；文案与操作对象冲突。
