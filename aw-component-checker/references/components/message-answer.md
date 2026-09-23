# Message Answer

Gallery ID: `message-answer` · 家族：Message

## Definition & Semantics

Message Answer 表示一条助手回复，将有顺序的正文、过程说明和自定义内容保留在同一条消息边界内。附件或产物补充回复结果，页脚提供整条回复的元信息与操作。

## When to Use

助手的同一轮回复包含连续或交错出现的文字、活动与结构化结果时使用。内容之间的先后关系影响理解时，应保留原有消息块顺序。

## When Not to Use

不要把所有会话内容合并为一条 Answer，抹除发言者与轮次边界。与当前回复无关的页面级状态或长期任务列表，也不应只因为来自系统就放进 Answer。

## Similar & Easily Misused Components

- [Message Query](message-query.md) 保留用户输入；Answer 承载助手输出。
- [Message Activity](message-activity.md) 解释回复过程与可展开详情，不替代最终结论。
- [Ask User](ask-user.md) 收集答案；可以嵌入回复，但仍具有独立的问答与提交职责。

## Composition

### Recommended

将 [Message Activity](message-activity.md) 放在对应过程的位置，用 [Message Media](message-media.md)、[Message Job Card](message-job-card.md) 或文件内容补充回复。整条消息保留一份 [Message Footer](message-footer.md)。

### Avoid

不要为同一回复的每个块再包一层完整 Answer 和页脚。不要把中途的提问或结果统一移动到最后，导致说明文字与对应内容脱节。

## Internal Usage

正文表达结论，Activity 表达过程，文件标识表达交付对象。document 块以只读方式呈现与 Composer 兼容的发送快照及行内引用，与 markdown、activity、custom 保持原数组顺序；引用状态与具体失效原因来自快照，不自动查询后台。共享图标与引用视觉，不添加编辑器工具栏或正文焦点入口。原 Markdown 渲染器、链接、代码与 custom 能力保留，不把富内容强制降级到 Composer schema。默认复制按顺序拼接 Markdown 块和 document 的文本／资源名称；如果“复制回答”应包括其他内容，调用方应提供明确的 copyText，不要假定自定义节点会被自动转为文字。custom 块的存在不赋予组件理解业务数据的能力。回答专属的次要命令可经 `footerMenuActions` 进入其 Footer 溢出 Menu；库只承接通用 label、icon 与回调，不推断 Job、Run 或目标路由。

## Examples

### Recommended

回复按顺序显示“正在分析”、相关活动、分析结论和导出的文件，页脚复制调用方定义的完整回答文本。

### Problematic

页面将工具执行详情作为最终回答正文，真正的结论藏在折叠区，用户难以确定助手已经得出什么结果。
