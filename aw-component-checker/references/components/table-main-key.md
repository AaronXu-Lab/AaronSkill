# Table Main Key

Gallery ID: `table-main-key`

## Definition & Semantics

Table Main Key 是对象表格中识别一条记录的主单元格，将名称、前置入口、类别标记和上下文操作围绕同一个对象组织。当前实现本身就是 Table Cell，且前置图形始终是必须提供回调的操作按钮。

## When to Use

当一列承担记录身份并需要前置预览、展开或打开入口时使用。名称和前置入口可以承担不同但清楚可辨的对象操作，例如展开目录与进入目录。

## When Not to Use

不要仅为了排列名称和图标而提供无实际行为的前置按钮。纯文本主列可使用普通 Table Cell；统计值或次要属性不应被包装成另一个行主标识。

## Similar & Easily Misused Components

[Table Cell](table-cell.md) 适合普通字段，Table Main Key 对行身份和前置操作有额外约束。[Grid Item Infos](grid-item-infos.md) 是卡片或列表对象的标题区，不产生表格单元格。[Table Main Key Badge](table-main-key-badge.md) 只补充主标识，不单独确定对象。

## Composition

### Recommended

直接作为 [Table](table.md) 记录行中的主列，按需组合 Table Main Key Badge。上下文 [Action Button](action-button.md) 或 [Menu](menu.md) 作用于该对象，行选择使用独立选择列。

### Avoid

不要在外面再包 Table Cell。避免前置图标看似展开但实际删除，或让名称点击同时进入详情和勾选记录。尾部操作不得切换到另一个对象的上下文。

## Internal Usage

名称必须足以区分记录；前置按钮名称与实际动作一致。badge 只补充来源、类别或状态。children 仅承载内容时不会自动获得导航行为，需要由调用方提供真实的链接或按钮。

## Examples

### Recommended

文件名称进入详情，前置预览按钮打开同一文件预览，尾部菜单提供该文件的重命名操作。

### Problematic

一个纯只读清单为每个文件图标提供空回调，只为复用 Table Main Key 的排列。
