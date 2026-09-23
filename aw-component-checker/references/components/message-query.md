# Message Query

Gallery ID: `message-query` · 家族：Message

## Definition & Semantics

Message Query 表示会话中的一条用户输入，保留用户表达与随消息关联的材料。消息可以由调用方标记为等待发送；组件本身不判断队列状态、编辑资格或发送结果。

## When to Use

内容已经作为一条用户消息进入会话记录，或进入调用方明确展示的待发送队列时使用。每条消息应具有可追踪的身份和清楚的用户来源。

## When Not to Use

不要用 Message Query 包装助手回复或系统运行详情。仍在编辑且尚未形成消息的文字应留在输入入口，不能仅为气泡外观而重复成一条已发送消息。

## Similar & Easily Misused Components

- [Message Answer](message-answer.md) 表示助手回复；区分依据是内容来源与职责。
- [Composer](composer.md) 收集可编辑草稿；Message Query 呈现已形成的消息条目。
- [Message Footer](message-footer.md) 为单条消息补充状态或操作，不替代消息正文。

## Composition

### Recommended

正文与文件或 [Message Media](message-media.md) 共同表达这次用户输入；页脚只操作所属消息。排队提示与激活时操作可以通过 footer、activeFooter 组合，业务资格和事件由调用方决定。

### Avoid

同一用户消息不要在正文、附件区域和相邻独立卡片中重复展示同一文件。也不要让同一份页脚状态或事件处理错误地作用于多条不同消息。

## Internal Usage

正文保留用户表达，附件标识对应实际材料。可选 document 直接接收 Composer 的发送快照，以只读方式呈现行内资源引用；引用可用状态、名称、具体失效原因与 occurrence 身份来自快照，不跟随后台变化，不把引用转换成附件或可编辑控件。renderResourceIcon 与 Composer 复用同一类型图标函数。默认复制在提供 document 时投影快照中的文本与资源名称，否则取 content；自定义页脚若改变复制范围，应保持说明一致。静态排队状态应表达状态，编辑和立即发送应表达操作，不能用可点击外观暗示不存在的处理。

## Examples

### Recommended

会话记录显示用户的问题及所附报告，页脚复制该问题；等待发送的另一条消息显示自身排队状态。

### Problematic

两条待发送消息共用未绑定消息 ID 的“取消”回调，取消第二条却移除了第一条。
