# Message Activity

Gallery ID: `message-activity` · 家族：Message

## Definition & Semantics

Message Activity 是消息内的过程说明，展示活动摘要、运行状态及可按需展开的文本详情。展开只影响详情可见性，不会启动、停止或批准活动。

## When to Use

助手回复需要解释正在发生或已经发生的过程，而完整记录不必持续展开时使用。只有确实存在补充详情时，摘要才应成为展开入口。

## When Not to Use

不要用 Activity 收集选择、提供任务批准，或把最终结果藏在过程记录中。只有一个无具体活动含义的等待指示时，也不必增加整套可展开结构。

## Similar & Easily Misused Components

- [Message Answer](message-answer.md) 承载回复结论与完整消息边界；Activity 是其中的过程内容。
- [Detail Activity](detail-activity.md) 表示对象详情中的活动记录；Message Activity 归属当前消息并可披露文本详情。
- [Spinner](spinner.md) 表示未知进度的等待，[Progress](progress.md) 表达持续任务的完成程度，也可明确表示程度尚不确定；Activity 提供具名活动及其解释，不能凭状态动画推导百分比。
- [Message Footer](message-footer.md) 适合消息级的紧凑状态和局部操作，不承载过程详情。

- [Message Job Card](message-job-card.md) 提出等待接受或拒绝的任务建议；Activity 解释实际发生的过程，展开记录不构成批准任务。

## Composition

### Recommended

在 Answer 的有序消息块中紧邻所解释的过程放置 Activity，最终结论继续由正文表达。需要用户回答时使用 [Ask User](ask-user.md)，使等待用户与展开记录形成不同职责。

### Avoid

不要为一个过程叠加多个重复的等待指示，却没有不同层级的对象可区分。

## Internal Usage

不要用同一摘要点击同时切换详情和执行重试。

摘要说明具体活动，详情补充依据或过程；状态与实际活动一致。stay 仅表示静态展示，不自动等于业务成功。空白详情不应承诺可展开内容；失败摘要应指向失败的活动，不能把局部失败扩大成整个会话已结束。

## Examples

### Recommended

“已检索 3 个来源”展开后列出来源说明，分析结论仍在回答正文中。

### Problematic

“查看执行详情”一经点击就重新执行任务，用户以为在阅读过程，实际触发了新操作。
