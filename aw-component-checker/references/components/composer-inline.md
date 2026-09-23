# Composer Inline

Gallery ID: `composer-inline` · 家族：Composer

## Definition & Semantics

Composer Inline 是紧凑的请求输入入口，激活后展示输入与操作区域。收起和展开只改变表达空间，不改变草稿、提交目标或请求语义。

## When to Use

会话或辅助面板需要常驻但低占用的输入入口，用户仍然能够辨认当前请求的上下文时使用。输入虽然从一行开始，仍可包含换行和较长文字。

## When Not to Use

不要将 Composer Inline 当作只接受单行的字段。用户需要同时审阅大量附件、复杂上下文或长篇草稿时，应优先考虑完整 Composer，而不是把决定提交含义的信息藏在收起区域。

## Similar & Easily Misused Components

- [Composer](composer.md) 是相同语义的完整结构，支持独立上下文栏和附件槽。
- [Input](input.md) 表达一个字段，不拥有会话请求的发送流程。
- [Composer Context Bar](composer-context-bar.md) 用于完整 Composer 的上下文；Inline 通过自身的 contextDropdown 提供上下文选择。

## Composition

### Recommended

需要显示附件时，调用方可在相邻区域组织 [Composer Attachment](composer-attachment.md)，并使附件归属与当前草稿明确关联。

### Avoid

不要同时在上下文栏和 Inline 内放置控制同一请求范围的两个选择器。完整与紧凑入口切换时，也不要保留两套同时可发送的独立草稿。

## Internal Usage

与 Composer 共用结构化 document、editorRef、原子引用和 @ 建议契约。紧凑布局不得将结构化草稿投影为字符串后再恢复引用；跨组件挂载时共享完整 document，editor-local 书签与撤销历史不跨挂载。需要在不重建编辑器的情况下切换布局时使用 Composer 的 variant。

将添加文件、授权入口与发送组合为同一请求的操作。

收起状态仍应能识别输入用途；展开后显示的权限与上下文必须与当前发送目标一致。文件接收回调不等于附件上传成功，发送按钮与输入提交必须采用同一有效性判断。组件不提供上传或任务执行服务。

## Examples

### Recommended

侧面板提供简洁的“描述需要调整的内容”入口，输入后展开操作区，发送到当前面板所属会话。

### Problematic

将“搜索文件”放进 Composer Inline，发送按钮一会儿搜索、一会儿创建任务，用户无法确定输入意图。
