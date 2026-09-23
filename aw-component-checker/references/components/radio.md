# Radio

Gallery ID：`radio`。

## Definition & Semantics

Radio 是互斥选择集合中的一个选项。同组至多一个选项被选中，组名称说明要决定的问题，选项名称说明可能答案。是否必须做出选择由任务决定。

## When to Use

当用户需要直接比较少量互斥答案，特别是各答案需要说明或有显著差异时使用。当前 Radio 需要由相应 RadioGroup 统一管理选择，不能靠彼此无关的选中样式模拟一组。

## When Not to Use

不要用单独一个 Radio 表示可随时开关的功能，也不要使用 Radio 选择允许并列成立的多项条件。点击选项执行删除等一次性命令不属于互斥选择。

## Similar & Easily Misused Components

- [Checkbox](checkbox.md) 允许多个选项同时成立；Radio 的选项相互排斥。
- [Dropdown](dropdown.md) 收起互斥值集合；Radio 让选项持续可见。
- [Segmented](segmented.md) 适合简短、少量、频繁切换的模式；需要详细比较答案或允许初始未选择时，Radio 更明确。
- [Switch](switch.md) 是一个状态对象的开关，不是多个答案之一。

## Composition

### Recommended

把 Radio 与同组说明放在一个清楚的问题下，在需要提交的表单中由 [Button](button.md) 统一提交。辅助描述可解释各答案差异，不能形成第二组隐藏选择。

### Avoid

不要将同一组 Radio 分散到互不关联的区域，也不要让选中某答案后又要求在旁边的 Dropdown 重复选择同一答案。

## Internal Usage

每个 Label 应表达一个答案，组标签表达共同问题。选项描述可以说明后果，但不能在 Radio 标签内嵌入会执行独立动作的按钮，造成选择与动作目标重叠。

## Examples

### Recommended

导出任务提供“仅当前页”和“全部结果”两个 Radio，用户选择范围后点击“导出”。

### Problematic

“包含附件”和“包含评论”本可同时选择，却被做成同组 Radio，导致用户无法表达需要的组合。
