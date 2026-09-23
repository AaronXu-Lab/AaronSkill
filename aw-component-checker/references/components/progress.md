# Progress

Gallery ID: `progress`

## Definition & Semantics

Progress 表达一个持续任务的完成程度，或者明确表达完成程度尚不可确定。Progress 陈述执行状态，不是用户可以拖动设置的值，也不负责实际执行任务。

## When to Use

任务存在可解释的总量与已完成量，用户需要持续理解完成程度时使用确定进度。进行中但无法计算比例时，可以采用组件支持的不确定状态，并明确任务仍在执行。

## When Not to Use

不要按等待时间伪造完成比例。存储占用、预算额度等静态测量不是任务完成度；多个独立待办的清单也不应仅靠进度条隐藏每项职责。

## Similar & Easily Misused Components

- [Spinner](spinner.md) 只说明局部任务仍在进行；Progress 更适合具有持续进度位置或真实比例的任务。
- [Skeleton](skeleton.md) 占位未来内容结构，不表达任务总量。
- [Guide Card](recommendation-panel.md) 引导若干独立事项并显示各项完成状态，Progress 表达一个任务的程度。
- [Detail Activity](detail-activity.md) 与 [Message Activity](message-activity.md) 解释事件或过程内容，Progress 不能代替这些说明。

## Composition

### Recommended

将 Progress 与任务名称放在同一任务范围内；取消操作由独立 [Button](button.md) 提供。任务失败时改为持续的 [Alert](alert.md) 或相应就地结果，而非永久停留在进度中。

### Avoid

不要给同一任务同时放置互不对应的 Spinner 和确定进度。多个阶段可以各有进度，但必须说明各自范围，不能把一个阶段的完成误报为全任务完成。

## Internal Usage

标签说明正在完成的任务，数值与总量采用同一口径。当前组件以 `value=null` 表达不确定状态，并内部管理标签、数值与轨道；不要引用已移除的独立 Progress 子部件。

## Examples

### Recommended

批量处理已有明确总数，Progress 根据实际已处理数量更新，并注明正在处理的任务。

### Problematic

长时间请求每秒增加一个百分点，达到 99% 后无限等待，使用户误以为存在真实进度。
