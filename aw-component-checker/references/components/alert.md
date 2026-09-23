# Alert

Gallery ID: `alert`

## Definition & Semantics

Alert 提供与当前页面、对象或任务持续关联的提示，说明需要关注的状态、影响或指导。Alert 不要求用户先作决定才能继续整个界面，也不等同于模态确认。

## When to Use

信息在用户继续处理当前对象时仍需保留，或者需要解释影响与恢复方式时使用。部分成功、授权失效和影响当前任务的限制都应明确关联到受影响范围。

## When Not to Use

不要把每次成功操作都保留为 Alert。单个字段的格式错误优先附着该字段；需要用户确认后才允许继续的决定，应评估 Dialog。普通永久介绍文字不因使用 Alert 外观就变成紧急通知。

## Similar & Easily Misused Components

- [Sonner](sonner.md) 提供短暂且非阻断的事件反馈；Alert 为需要持续保留的上下文信息提供位置。
- [Badge](badge.md) 概括对象状态，Alert 解释状态的影响或下一步。
- [Empty State](empty-state.md) 说明已经确认的内容空缺，Alert 可以说明请求失败，不能将失败伪装成无内容。
- [Dialog](dialog.md) 聚焦一次决定；Alert 允许用户在当前内容中继续判断。

## Composition

### Recommended

按 Detail Page Structure 将对象级 Alert 与 [Detail Hero](detail-hero.md) 关联。恢复操作使用 [Button](button.md)，操作对象与提示范围一致；字段级问题保留字段说明，Alert 只在需要时补充整体影响。

### Avoid

不要让 Alert 与 Sonner 长期重复播报同一个结果，或在 Alert 中放置与当前问题无关的全局操作。关闭提示不能被误解为问题已经解决。

## Internal Usage

主要文字说明发生了什么，补充说明提供影响或处理条件，操作回应同一问题。当前实现默认采用 `role="alert"`；静态中性指导不应仅因组件名称就被当作需要打断播报的警报，调用方可按实际语义调整原生角色。

## Examples

### Recommended

对象详情持续显示“连接已失效”，说明任务暂停，并提供重新连接操作。

### Problematic

请求失败后显示“暂无记录”的空态，只在短暂 Sonner 中提及错误，用户无法持续获知失败原因。
