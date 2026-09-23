# Detail Activity

Gallery ID: `detail-activity`

## Definition & Semantics

Detail Activity 表达对象历史中的一个事件，通过事件标题、补充说明和时间说明发生了什么。尾部状态和操作继续属于该事件，不代表整个对象的全部状态。

## When to Use

当用户需要回溯单次变更、执行或其他有时间上下文的活动时使用。一个条目应对应一个可以独立理解的事件。

## When Not to Use

不要将尚未发生的推荐任务写成已发生的历史。仅表达总体加载进度或静态对象属性时，不需要活动行。

## Similar & Easily Misused Components

[Detail Activity Group](detail-activity-group.md) 管理多条事件的组合关系。[Message Activity](message-activity.md) 依附单条会话消息并可展开支撑细节；Detail Activity 依附对象历史。[Progress](progress.md) 表达任务进行程度，不能代替事件记录。

## Composition

### Recommended

放入 Detail Activity Group，必要时在尾部组合 [Badge](badge.md) 表达事件结果，或 [Button](button.md) 查看该次事件详情。当前行本身不自动提供详情折叠，应由调用方选择明确入口。

### Avoid

不要把事件级失败与对象整体不可用混为一谈。避免查看某次活动的按钮同时重跑整个对象任务；操作目标不同必须清楚区分。

## Internal Usage

标题说明事件，描述补充结果或过程，时间对应该事件发生时刻。operator 与 operation 等兼容字段不能让操作者、动作和结果混淆；省略时间展示时，仍应有可理解的上层时间上下文。

## Examples

### Recommended

“第 12 次运行”显示“写入步骤失败”、发生时间和“查看记录”入口，入口打开该次运行。

### Problematic

最新一次运行失败后，把所有历史条目的状态都显示为失败，使历史事实随当前对象状态改变。
