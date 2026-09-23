# Input Area

Gallery ID：`input-area`。

## Definition & Semantics

Input Area 接受一个字段的多行文本，保留段落和换行的输入意图。当前实现是原生 textarea 的封装，发送、保存及业务校验由调用方负责。

## When to Use

当内容允许多行表达，例如说明、备注或可编辑的提示文本时使用。用户需要表达段落结构时，即使初始内容很短，也具备多行输入的条件。

## When Not to Use

不要因为单行名称比较长就改用多行字段。需要富文本排版、媒体编辑或结构化文档编辑时，Input Area 本身没有这些能力。纯阅读区域不应为了获得边框而采用文本输入控件。

## Similar & Easily Misused Components

- [Input](input.md) 负责单行值；Input Area 负责允许换行的文本值。
- [Composer](composer.md) 面向提交或发送内容，并组织附件和操作；Input Area 是可嵌入任意表单的文本字段。
- [Code Block](code-block.md) 负责代码阅读与复制，不是多行编辑字段。

## Composition

### Recommended

在表单或详情编辑区中配合明确的 [Button](button.md) 保存与取消；输入内容作为该字段的草稿。若需要发送附件和上下文，可由 Composer 组织，而不是在多个表单字段间重复建立发送区。

### Avoid

不要同时用 Input Area 和 Composer 编辑同一份正文却保留两套独立草稿或发送入口。不能把多行输入的换行无提示地解释为提交，使用户失去段落表达。

## Internal Usage

字段名称说明内容用途，辅助说明解释允许填写的内容。当前 editable=false 或 readOnly 会使输入区域退出焦点并阻止编辑，不能把该行为当作“仍可按原生只读文本框方式聚焦复制”的承诺；需要稳定阅读或复制时，应明确提供内容展示与操作。

## Examples

### Recommended

对象说明在 Input Area 中编辑，“保存说明”只提交该字段；取消恢复原值。

### Problematic

把不可编辑的使用指南放进 Input Area，并要求用户通过聚焦字段复制内容，实际控件会失焦，阅读任务与组件行为不符。
