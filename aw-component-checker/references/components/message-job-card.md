# Message Job Card

Gallery ID: `message-job-card` · 家族：Message

## Definition & Semantics

Message Job Card 是消息中可接受或拒绝的任务建议，将拟创建的任务、支持该建议的依据和推荐理由组织为一次明确决策。组件展示调用方提供的决策结果，不自行创建任务。

## When to Use

助手提出一个与当前会话相关的可追踪任务，用户需要理解为何创建并决定是否接受时使用。建议应具备足够清楚的目标，而不是只有模糊的下一步口号。

## When Not to Use

不要用此卡片充当所有任务的目录、执行进度或任意内容推荐。没有创建或拒绝的实际处理时，卡片不能宣称建议已经执行。

## Similar & Easily Misused Components

- [Guide Card](recommendation-panel.md) 展示一组可分别完成的引导事项，Job Card 针对一项建议做接受或拒绝决策。
- [Message Activity](message-activity.md) 说明已经发生或正在发生的过程，Job Card 提出尚待决策的任务。
- [Dialog](dialog.md) 用于独立的确认任务；Job Card 保留建议与消息的上下文，不能代替确实需要额外确认信息的流程。

## Composition

### Recommended

在 [Message Answer](message-answer.md) 中紧邻提出建议的说明展示卡片。创建成功后由调用方更新结果；存在已创建对象时提供查看入口。

### Avoid

不要在同一消息正文、卡片和页脚同时放置三套等价的“创建任务”。接受卡片若只打开后续配置，也不要立即显示“已创建”，造成结果提前承诺。

## Internal Usage

标题识别拟创建的任务，proof 提供支持依据，reason 解释该依据为何支持建议。接受、拒绝、已创建与查看分别对应决策、结果和导航；拒绝建议不代表删除已有任务。调用方更新 accepted 时应已有与结果文案一致的事实。

## Examples

### Recommended

助手建议建立每周汇总任务，卡片说明数据来源与周期需求，用户创建后可查看已创建的任务。

### Problematic

卡片只写“提升效率”，点击勾号即显示“已创建”，实际没有任务目标，也没有创建结果。
