# Switch

Gallery ID：`switch`。

## Definition & Semantics

Switch 控制一个明确功能、能力或偏好的开启与关闭状态。开关的对象保持不变，当前位置表达该对象的布尔状态；Switch 不表达部分开启。

## When to Use

当用户可以主动开关某项功能，并能理解开关如何生效时使用。即时生效的设置最符合开关预期；如需统一保存，界面必须明确区分待保存值与当前实际状态。

## When Not to Use

不要把服务连接、运行成功或健康状态做成不能控制的 Switch。接受协议、选中待处理记录、多个互斥模式也不应仅因数据是布尔值就使用开关。

## Similar & Easily Misused Components

- [Checkbox](checkbox.md) 关注对象或条件是否选中；Switch 关注功能是否开启。
- [Radio](radio.md) 和 [Segmented](segmented.md) 在多个互斥取值之间选择；Switch 只有同一对象的开启与关闭。
- [Badge](badge.md) 可展示只读状态，不暗示用户能够改变状态。

## Composition

### Recommended

与 [Item](item.md) 的设置名称和说明组合，让状态对象与控制明确关联。开关启用后才有意义的下级设置可以从属展示，但父开关不能悄悄改写下级设置的含义。

### Avoid

避免在同一区域同时提供一个 Switch 和一组“开启／关闭”按钮控制同一功能。开关变更只保存草稿时，不要同时把另一处状态标签更新为“已生效”。

## Internal Usage

Label 应保持为被控制的功能名称，不随状态在“开启通知”和“关闭通知”之间切换。状态文字可以补充真实状态；说明应交代影响对象和必要的生效条件。

## Examples

### Recommended

“桌面通知”旁的 Switch 开启后启用通知，Label 仍为“桌面通知”。

### Problematic

列表用 Switch 展示“服务器在线”，但用户无权控制服务器连接，开关制造了错误的可控预期。
