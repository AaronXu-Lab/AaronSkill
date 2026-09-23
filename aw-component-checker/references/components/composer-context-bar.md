# Composer Context Bar

Gallery ID: `composer-context-bar` · 家族：Composer

## Definition & Semantics

Composer Context Bar 是请求输入的上下文容器，通过一个选择器表明当前草稿将在哪个范围内使用。选择改变待提交请求的上下文，不代表立即发送请求。

## When to Use

完整 Composer 的请求范围可选择，且用户需要在发送前辨认或调整该范围时使用。选项和选中状态由调用方提供。

## When Not to Use

不要用上下文栏放置发送记录、会话统计或任意工具集合。没有可表达的上下文时，不应仅为了增加底板而显示空栏。

## Similar & Easily Misused Components

- [Dropdown](dropdown.md) 提供选择能力；Context Bar 将该能力限定到请求上下文，不是通用的筛选栏。
- [Composer Inline](composer-inline.md) 使用自身的 contextDropdown；独立 Context Bar 属于完整 [Composer](composer.md) 的组合。
- [Session Info](session-info.md) 说明现有会话的属性，不选择当前请求的目标。

## Composition

### Recommended

将 Context Bar 放在所属 Composer 的结构内，并让 Dropdown 的当前值与发送处理采用相同上下文。其他恢复入口由调用方放入适当的相邻结构，保持职责可辨认。

### Avoid

不要同时在栏内和发送按钮旁放置控制同一范围的选择器。当前公开结构只提供前置 Dropdown，不应把 Context Bar 当作具有任意尾部操作槽的工具栏。

## Internal Usage

选项应属于同一个上下文维度，例如目标项目。当前值必须表达实际选择的范围；不要将“新建”“删除”等立即执行操作混入普通上下文值，使选择结果含义不确定。

## Examples

### Recommended

用户在输入请求前选择目标项目，后续提交使用所选项目作为上下文。

### Problematic

上下文栏显示项目 A，发送处理却始终使用项目 B；栏内选择没有控制所宣称的范围。
