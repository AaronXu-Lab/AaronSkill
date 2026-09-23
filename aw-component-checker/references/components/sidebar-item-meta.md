# Sidebar Item Meta

Gallery ID: `sidebar-item-meta`

## Definition & Semantics

Sidebar Item Meta 是依附 Sidebar Item 的紧凑补充信息，说明该入口或对象的短状态。当前实现是行内展示元素，不是独立弹出层；是否常驻或在 hover 时出现由 Sidebar Item 决定。

## When to Use

当侧栏主标签需要简短限定信息，且该信息有助于理解同一个对象的当前情况时使用。

## When Not to Use

不要在 Meta 中放主导航名称、长篇说明或必需操作。需要跨多行说明对象上下文时，单个紧凑标记不足以承担该任务。

## Similar & Easily Misused Components

[Badge](badge.md) 提供通用状态和类别标签，Sidebar Item Meta 依附侧栏行的尾部约定。[Session Info](session-info.md) 提供会话的多项补充信息；Meta 不会自动展开成 Session Info。[Sidebar Item](sidebar-item.md) 仍负责主入口和显隐。

## Composition

### Recommended

通过 Sidebar Item 的 metadata 尾部组合，保持补充信息归属于同一条目。按 Sidebar Statements Scenario，同类会话可根据待处理与当前选中状态选择显示信息，不能把该特定映射推广为所有对象的规则。

### Avoid

不要在主标签旁和 Meta 中重复同一名称。避免让 Meta 外观暗示可点击而实际没有动作，或用一段临时 hover 信息替代任务必须持续可见的关键信息。

## Internal Usage

内容应能被理解为状态或限定信息，例如“待确认”。不要在标记内部放菜单、输入框或多个相互独立的控件；当前组件不提供这些交互的结构。

## Examples

### Recommended

会话名称旁的“待确认”说明该会话需要处理，主入口仍用于打开会话。

### Problematic

将完整会话摘要塞进 Meta，并把这个行内元素视为已经实现的可展开预览浮层。
