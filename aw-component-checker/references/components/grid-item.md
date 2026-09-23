# Grid Item

Gallery ID: `grid-item`

## Definition & Semantics

Grid Item 表达一个可识别的对象及其摘要、最近动态和对象操作。card 与 list 是同一对象结构的排列方式，不会自动改变对象身份、选择含义或业务行为。

## When to Use

当用户主要按名称、描述和对象状态浏览一组同类对象，并需要进入详情或对对象执行局部操作时使用。也可在外层明确建立选择模型后呈现内容丰富的候选项。

## When Not to Use

需要逐列比较多项属性时，使用 Table。不要把每个普通设置行都包装成对象卡片；Grid Item 的容器也不会因为存在 onClick 就自动成为完整链接或选择控件。

## Similar & Easily Misused Components

[Table](table.md) 支持跨对象属性比较；Grid Item 优先支持逐对象识别。[Item](item.md) 适合单条信息或设置。[Grid Item Infos](grid-item-infos.md) 是 Grid Item 内的身份区，不能代替整体对象结构。

## Composition

### Recommended

用 Grid Item Infos 提供标题和辅助身份，按需组合 [Symbol](symbol.md)、[Badge](badge.md) 和 [Menu](menu.md)。按照 Multiple Entry Select Scenario，在 [Sheet Basic](modal-panel.md) 中由外层管理候选集、选择状态和确认，Grid Item 仅呈现每个候选对象。

### Avoid

不要让整卡点击既导航又改变选择，除非产品提供明确的模式和目标区分。不要将局部 Switch、菜单或最近动态按钮的动作误传给整卡导航。外层选择模式中不应同时保留会把用户带离任务的默认导航。

## Internal Usage

标题、图标、摘要、动态和尾部操作必须属于同一个对象。recent 是对象的最近活动，meta 是补充属性；不要在这些位置塞入另一个对象的主身份。当前组件仅隔离部分尾部及 recent 操作，调用方仍需保证完整的操作语义。

## Examples

### Recommended

自动任务卡片展示任务名称、执行规则和最近运行，Switch 控制该任务启停，点击最近运行进入对应记录。

### Problematic

在多选候选弹窗中，点击卡片一边勾选对象，一边立即跳到对象详情，导致确认任务被中断。
