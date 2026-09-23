# Guide Card

Gallery ID: `recommendation-panel`

## Definition & Semantics

Guide Card 组织若干引导事项，并区分尚可进入的事项与已完成的事项。当前未完成行是调用外部行为的入口，完成行是只读状态；组件不自行导航、判定完成或计算下一步。稳定 Gallery ID 沿用 recommendation-panel。

## When to Use

用户需要理解一组相关的后续事项，并能够分别进入未完成事项对应的任务时使用。完成状态必须来自可说明的实际结果，调用方负责将每个入口连接到适当任务。

## When Not to Use

不要用 Guide Card 收集用户当场勾选的选择或同意，也不要把点击事项本身当成完成。需要强制先后验证、禁用尚未解锁事项或重新进入已完成事项时，不能假定当前组件已经提供这些能力；应选择能表达相关约束的任务结构。

## Similar & Easily Misused Components

- [Checkbox](checkbox.md) 让用户改变选择；Guide Card 的完成标记陈述事实，不能作为勾选控件使用。
- [Progress](progress.md) 表达一个任务的完成程度；Guide Card 保留多个事项各自的身份和完成状态。
- [Message Job Card](message-job-card.md) 在消息中提出一项可接受或拒绝的任务建议；Guide Card 组织一组可分别进入的引导事项。
- [Ask User](ask-user.md) 收集问题答案；Guide Card 的事项入口不提交答案。

## Composition

### Recommended

将卡片放在与引导目标相关的产品区域，由调用方决定显示、关闭和事项导航。事项入口可以进入相应页面或适当的任务界面，任务真实完成后再更新对应状态。关闭卡片只处理显示，不替代完成任务。

### Avoid

不要在只读完成标记上叠加独立 Checkbox 或“手动完成”交互，使一个事项同时拥有两种完成依据。不要另设一个同名“下一步”控制器却进入不同事项；当前 Guide Card 没有底部按钮或自动下一项模型，不应依据旧示例假定存在。

## Internal Usage

标题说明这组事项的共同目标，每行名称应让用户理解将进入什么任务；完成标记与该事项真实结果对应。未完成行的图形与尾部箭头辅助表达入口，已完成行不继续暗示可点击。装饰图片不承载额外任务、状态或操作，事项 ID 与外部处理目标应保持一致。

## Examples

### Recommended

初次使用引导列出“创建项目”和“连接数据源”；点击未完成事项进入对应流程，流程完成后由应用更新该事项状态。用户关闭卡片不会把剩余事项标为完成。

### Problematic

用户只点击了“连接数据源”，尚未完成授权，界面就把该行标记为完成；状态表达了一个未发生的结果。
