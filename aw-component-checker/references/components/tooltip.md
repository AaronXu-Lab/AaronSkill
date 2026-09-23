# Tooltip

Gallery ID：`tooltip`。

## Definition & Semantics

Tooltip 在用户悬停或聚焦某个目标时，提供与该目标直接相关的简短补充说明。Tooltip 的职责是解释，内容本身不建立新的交互任务。

## When to Use

当图标、术语或紧凑控件需要可按需查看的说明，而用户无需依赖该说明才能完成关键步骤时使用。展开被截断的非交互文本也可使用，但内容仍应属于同一目标。

## When Not to Use

不要把关键错误、必须确认的风险、修复按钮或输入控件放进 Tooltip。需要用户主动进入并操作的浮层，应采用与该任务匹配的结构；不能依赖提示短暂显示来承接操作。

## Similar & Easily Misused Components

- [Menu](menu.md) 承载可执行条目；Tooltip 承载目标说明。
- [Sonner](sonner.md) 由事件结果触发反馈；Tooltip 由查看目标触发解释。
- [Alert](alert.md) 保留必须看见的状态或指导，Tooltip 不适合独自承担这些信息。
- [Content Group](content-group.md) 可以借 Tooltip 展开隐藏的紧凑内容；这是宿主与说明浮层的组合，不是两种可互换的控件。

## Composition

### Recommended

将 Tooltip 关联到已有明确职责的 Button 或信息目标，目标继续承担原本操作。Content Group 使用 Tooltip 展示溢出内容时，隐藏内容应保持只读。

### Avoid

避免 Tooltip 与可操作菜单共享内容却分别维护开合，或在 Content Group 的隐藏内容中放入必须点击的移除按钮。已经有持久错误说明时，Tooltip 可以补充细节，但不能成为唯一恢复路径。

## Internal Usage

说明应补充目标含义，不能把目标名称原样重复作为唯一内容。Tooltip 内的文字、图标都应解释同一目标，不嵌入会争夺焦点的操作；当前实现也不提供独立的任务内容契约。

## Examples

### Recommended

图标按钮的名称为“复制链接”，Tooltip 补充快捷键；复制动作仍发生在按钮上。

### Problematic

上传失败后只在悬停 Tooltip 中提供“重试”按钮，错误和恢复入口无法持续访问。
