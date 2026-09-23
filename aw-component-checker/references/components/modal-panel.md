# Sheet Basic

Gallery ID：`modal-panel`。

## Definition & Semantics

Sheet Basic 提供模态临时工作区，用来搜索、浏览、选择或管理一组对象。标题栏、工作内容和可选操作区共同维持一个任务上下文。Gallery ID 保留 modal-panel，当前公开组件名为 SheetBasic。

## When to Use

当用户需要在原上下文中短暂进入一个可持续操作的工作区，再带着结果返回时使用。对象列表、搜索和选择需要共享任务范围时，比单次确认更符合 Sheet Basic。

## When Not to Use

一段短确认不需要仅为更大容器而使用 Sheet Basic。长期驻留、跨页面引用或持续对照背景内容的任务，不适合当前模态工作区。文件全屏预览也不应默认重建成普通任务 Modal。

## Similar & Easily Misused Components

- [Dialog](dialog.md) 与 [Dialog Basic](dialog-basic.md) 围绕紧凑决定或说明；Sheet Basic 围绕临时工作区。
- [Lightbox](lightbox.md) 聚焦文件预览、相邻文件与下载；Sheet Basic 承载任务操作和结构化内容。
- [Modal Actions](modal-actions.md) 负责该工作区底部的操作分组，不能替代工作区本身。

## Composition

### Recommended

使用 [Topbar](topbar.md) 提供工作区身份或搜索，正文由 [Table](table.md)、[Selection Tree](selection-tree.md) 或 [Grid Item](grid-item.md) 展示候选对象。选择集合留在工作区中，底部 Modal Actions 提交集合或取消。

### Avoid

避免同时提供两处同范围搜索，或者标题栏和底部各自维护一套不同的选中数量。嵌套确认仅在子决定确有必要时使用，不应把每次普通选项切换都变成第二个模态任务。

## Internal Usage

标题、搜索范围、正文对象与确认文案应指向同一任务。隐藏操作区应意味着任务不需要集中提交或已有明确完成方式。当前默认确认按钮只负责关闭；调用方必须提供实际提交行为，不能将默认入口当作已实现保存。

## Examples

### Recommended

资源选择工作区展示可搜索对象和暂选数量，用户确认后一次提交所选对象。

### Problematic

Modal 标题为“选择文件”，搜索却查询全局成员，底部“确认”只关闭窗口而不提交选择。
