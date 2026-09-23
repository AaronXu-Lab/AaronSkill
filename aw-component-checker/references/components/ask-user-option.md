# Ask User Option

Gallery ID: `ask-user-option` · 家族：Ask User

## Definition & Semantics

Ask User Option 表示当前问题的一项候选答案，或表达自定义回答的输入位置。选中状态表示该答案参与当前回答，不表示任务已经执行或事项已经完成。

## When to Use

在 Ask User 的题目上下文中，问题具有可列出的答案或需要保留自由补充渠道时使用。每个预设答案应拥有稳定值和可辨认的含义。

## When Not to Use

不要将选项脱离问题单独用作操作按钮或跳转卡片。也不要把“运行”“删除”等即时操作伪装成答案选择，使用户无法区分回答问题与执行任务。

## Similar & Easily Misused Components

- [Radio](radio.md) 提供一般互斥选择；Ask User Option 在问答序列中还参与当前题和前进逻辑。
- [Checkbox](checkbox.md) 提供独立或多选条件；Ask User Option 的多选范围由所属问题决定。
- [Ask User Option Symbol](ask-user-option-symbol.md) 只表示答案标识与选中状态，不替代答案文字。
- [Ask User](ask-user.md) 提供完整问答结构，Option 不能独立决定提交范围。

## Composition

### Recommended

在同一 Ask User Item 下组织回答同一问题的选项，并保持题目和选项的选择模式一致。常规 Ask User Options 已追加自定义回答输入；调用方提供该输入的说明即可。

### Avoid

不要在已有自动追加输入的 Options 中再放一个等价的“其他”输入项，造成两个自定义答案入口。

## Internal Usage

选项内部不要嵌入执行不同操作的按钮，使整行选择与内部操作争夺同一次激活。

答案文字必须回应题目，补充说明用于区分选项而不是提出另一个问题。单选项之间应可作明确取舍，多选项应允许合理并存。选择标识与提交值保持一致；当前预设单选项会触发前进，多选项需要保留继续选择的机会。

## Examples

### Recommended

“需要哪些输出格式？”使用多选答案“PDF”和“电子表格”，并保留一个自定义回答入口。

### Problematic

题目允许多个答案，却把 Option 配成单选自动前进，用户选择第一个格式后失去继续选择的机会。
