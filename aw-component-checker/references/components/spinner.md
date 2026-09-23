# Spinner

Gallery ID: `spinner`

## Definition & Semantics

Spinner 表示某个可识别的局部任务仍在进行，完成时间或比例未知。旋转本身不表达成功、失败、排队顺序或系统健康。

## When to Use

控件或局部区域正在异步处理，用户需要知道操作已被接收时使用。任务范围应能从触发控件、对象或邻近文字中识别。

## When Not to Use

不要用持续旋转代替已知进度。结果已失败或完成时应结束等待表达；长期后台在线状态也不应冒充正在执行的局部任务。

## Similar & Easily Misused Components

- [Progress](progress.md) 可以表达真实完成比例；Spinner 不具有数值含义。
- [Skeleton](skeleton.md) 表达即将出现的内容结构；Spinner 表达当前进行中的处理。
- [Empty State](empty-state.md) 表达已确认的空结果；Spinner 表达结果尚不可知。
- [Message Activity](message-activity.md) 表达消息内的过程与详情，不能只用 Spinner 替代过程含义。

## Composition

### Recommended

在 [Button](button.md) 的处理状态或某条记录旁组合 Spinner，由调用方保留明确的操作或任务名称。任务结束后使用适当的结果反馈；需要跨区域告知时再考虑 [Sonner](sonner.md)。

### Avoid

不要因一个局部请求未完成就让整页各处都旋转。不要在已经自行表达生成状态的 Message Activity 旁重复添加无新增信息的 Spinner。

## Internal Usage

提供的名称应说明正在等待什么；有邻近状态文字时，Spinner 可以只作装饰。组件不自带超时、取消、完成或错误切换，调用方必须提供真实的生命周期。

## Examples

### Recommended

邀请操作提交后，在该操作处保留“正在邀请”并显示 Spinner，其他可用区域仍可操作。

### Problematic

连接已失效但仍显示 Spinner，使用户继续等待一个不会自行完成的过程。
