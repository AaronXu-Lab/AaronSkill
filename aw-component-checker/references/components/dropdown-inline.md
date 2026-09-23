# Dropdown Inline

Gallery ID：`dropdown-inline`。

## Definition & Semantics

Dropdown Inline 表达紧凑宿主中的预定义单值选择。整条 24px rounded 触发器同时显示当前值并打开选择浮层；它保留 Dropdown 的选择语义，但不承担完整表单字段的标签、说明、尺寸、宽度或校验状态。

## When to Use

当属性面板、工具条或其他高密度区域需要让用户直接修改一个短值，并且宿主已经清楚说明选择维度时使用。选项集合应明确、无需搜索，当前值与 caret 必须共同位于整条可点击触发器内。

## When Not to Use

需要可见字段标签、帮助或错误信息、不同字段宽度、常规输入高度或复杂选项说明时使用 [Dropdown](dropdown.md)。大量选项需要过滤时使用 [Combobox](combobox.md)。若触发器只表示“打开一组操作”而不显示当前值，应使用 [Action Button](action-button.md) 与 [Menu](menu.md)，不能把动作菜单冒充选择字段。

## Similar & Easily Misused Components

- [Dropdown](dropdown.md) 是完整选择字段；Dropdown Inline 是固定 24px、固定 rounded、内容自适应的紧凑选择器。
- [Action Button](action-button.md) 触发局部动作；Dropdown Inline 的整条触发器表达并修改当前值，caret 不是独立操作。
- [Menu](menu.md) 以当前上下文可做什么为核心；Dropdown Inline 的浮层选项属于同一选择维度。
- [Combobox](combobox.md) 允许输入文字过滤预定义候选项；Dropdown Inline 的触发器不可编辑。

## Composition

### Recommended

由宿主在相邻位置提供属性名称或选择范围，Dropdown Inline 只显示短当前值与 caret。多个实例并列或成组时保持同一 24px 高度，并让每个可访问名称明确指出所属属性。作为 [Detail Field](detail-field.md) 的 dropdown value 时，由 Detail Field 外层补偿其 6px 起始内边距，不改变 Dropdown Inline 本体。

### Avoid

不要在组件内部重复宿主已经提供的 Label，也不要在 24px 触发器中加入前置图标、说明、清除按钮或独立 caret 点击区。不要通过短触发器压缩选项浮层；浮层继续保留 Dropdown 的可用宽度。

## Internal Usage

触发器固定使用 24px 高度与 rounded 小圆角，当前值使用 Body MD；起始侧 padding、gap、16px 图标及 hover、focus 反馈沿用 Action Button 默认规格，尾侧 padding 固定为 4px，与 16px caret 在 24px 高度内的上下留白一致。Inline 控件按下时保持位置与尺寸稳定，不采用缩放反馈。整条触发器可点击，当前值单行展示，caret 与文字属于同一选择入口。选项、选中标记、键盘选择、受控与非受控值沿用 Dropdown；公开设计轴仅保留 disabled，固定几何不是可配置属性。

## Examples

### Recommended

DS Panel 的 `info` 属性在相邻属性名之后显示值 `text` 与 caret；点击触发器任意位置打开 `text`、`text + description` 选项，选择后整条触发器更新当前值。

### Problematic

把 24px 触发器扩展成带 Label、错误说明、前置图标和清除按钮的完整字段，同时允许调用方切换 capsule 与 rounded；紧凑选择器被重新变成一套重复且组合失控的 Dropdown。
