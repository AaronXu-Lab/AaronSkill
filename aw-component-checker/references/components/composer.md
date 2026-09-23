# Composer

Gallery ID: `composer` · 家族：Composer

## Definition & Semantics

Composer 是会话或任务的自由表达入口，将尚未提交的文字、附加材料与提交操作组织成同一份输入。Composer 负责输入结构；发送、上传、执行权限与任务状态由调用方管理。

## When to Use

用户需要描述目标、约束或补充上下文，并将这些内容作为一次请求提交时使用。存在较长草稿、附件或独立上下文选择时，完整 Composer 更容易表达输入范围。

## When Not to Use

不要用 Composer 编辑名称或普通表单字段；这些内容依赖表单提交，不是独立的会话请求。搜索现有对象也不应因为包含文字和按钮就采用 Composer。

## Similar & Easily Misused Components

- [Composer Inline](composer-inline.md) 保留相同提交意图，适合紧凑入口；完整 Composer 提供附件槽与独立上下文栏。
- [Input Area](input-area.md) 收集一个多行字段；Composer 组织一次完整请求。
- [Ask User](ask-user.md) 收集当前问题所需的结构化答案，Composer 允许用户自行组织请求。
- [Message Query](message-query.md) 呈现进入会话的用户内容；Composer 保存可编辑草稿。

## Composition

### Recommended

使用 [Composer Context Bar](composer-context-bar.md) 界定请求的上下文，用 [Composer Attachment](composer-attachment.md) 表示随请求提交的文件。文件入口、授权设置与发送操作应作用于同一份草稿。

### Avoid

同一请求不要同时出现两个拥有独立草稿与提交行为的 Composer。当前会话不能继续时，应由 [Session End](session-end.md) 解释边界，避免仍保留看似可发送的入口。

## Internal Usage

`document/onDocumentChange` 提供结构化草稿；提供 document 时优先于字符串 value，onValueChange 可接收纯文本投影。资源引用是具有独立 occurrenceId 的原子节点；重复资源不是同一节点，不能用显示名称或正文字符串重建身份。资源目录、搜索、最近记录、可用性刷新和发送契约仍由调用方管理。

Plus 打开前通过 editorRef 捕获选区书签；确认在映射后的选区末尾插入且保留选区原文。插入点左右都是正文且左侧尚非空白时，在首个引用前补一个普通空格；每个引用后始终补一个空格，整批仅占一次撤销步骤。取消只释放书签，不修改文档。仅新输入的 @ 可在正文/段落开头、显式 hardBreak 后或前有普通空格时触发；删除后续文字而重新暴露旧 @ 不创建新建议会话。紧邻正文、邮箱、仅 Tab、视觉自动折行与资源原子紧后不触发。组合输入期间抑制；确认仅替换对应 @query，保留前面的空格与换行。“更多”打开 Sheet 时保留 suggestion.confirm，取消才 close，不能用字符串查找代替选区事务。

不可用引用以删除线和 Tooltip 原因表达状态，并支持键盘读取；名称不可编辑。结构化复制粘贴保留资源信息，新副本具有独立 occurrenceId；外部纯文本仅包含显示名称。外部草稿替换清空历史和书签；Composer variant 切换保留同一编辑器，跨组件重新挂载则需应用共享受控文档。

输入提示应说明用户可以表达的内容，发送按钮应提交当前文字及附件。发送与停止代表不同操作，调用方需要按实际状态决定当前可用操作。上下文选择不得暗中改变历史消息的归属；授权入口也不应与另一处控制同一权限的按钮重复。

## Examples

### Recommended

用户输入“比较这两份报告”，添加两份文件，在同一 Composer 中发送。

### Problematic

页面用 Composer 收集项目名称，旁边另有“保存项目”按钮；Composer 的发送箭头没有独立请求可提交。
