# Ask User Option Symbol

Gallery ID: `ask-user-option-symbol` · 家族：Ask User

## Definition & Semantics

Ask User Option Symbol 是答案前置的标识与选择反馈，表示编号或自定义回答，并与所属选项的选中状态一致。默认仅作展示；有独立意义的选择入口时才成为可操作控件。

## When to Use

Ask User 的选项需要显示编号、自定义回答标记或对应选中状态时使用。自定义答案已经填写后，可以用独立标识入口重新选回该答案。

## When Not to Use

不要因其外观紧凑就用于通用编辑、任意编号列表或步骤完成标记。没有独立操作需求时，不应把纯标识变成额外按钮。

## Similar & Easily Misused Components

- [Ask User Option](ask-user-option.md) 表达完整答案并管理选择目标；Symbol 只承担其中的前置标识。
- [Symbol](symbol.md) 识别一般对象或类别；Ask User Option Symbol 识别问答选项并反映选择状态。
- [Action Button](action-button.md) 执行局部操作；此处的铅笔标识通常指向自定义回答，不自动代表编辑任意对象。

## Composition

### Recommended

让 Symbol 与对应 Option 或自定义输入共同表达同一份答案。普通选项由整行完成选择，Symbol 保持展示；已有自定义答案需要重新选择时，独立入口与该输入共享答案状态。

### Avoid

不要在已承担整行选择的选项里增加第二个互相独立的选择按钮。也不要让 Symbol 的选中状态与行或输入的实际提交状态分别维护，形成两个冲突结果。

## Internal Usage

编号与当前问题的答案顺序一致，图标表示自定义回答。可操作时，操作说明应明确“选择已有自定义答案”等真实意图；选择反馈不应被理解成答案正确或任务成功。单独展示 Symbol 不能代替完整答案标签。

## Examples

### Recommended

用户先填写自定义答案，再暂时选择预设项；点击自定义答案前的标识重新选回已填写内容。

### Problematic

选项未参与提交，但前置 Symbol 显示选中；用户以为答案已经保留，提交结果却没有该答案。
