# Checkbox

Gallery ID：`checkbox`。

## Definition & Semantics

Checkbox 表达是否选择一个对象或条件。多个 Checkbox 可以同时成立；混合态表达一个明确集合中只有部分成员被选择，而不是第三个普通业务选项。

## When to Use

当用户可以独立选择多条记录、勾选若干条件或确认一项同意声明时使用。全选控件可以汇总并控制一组子项，但集合范围必须明确。

## When Not to Use

不要把“处理中”“未知”等对象状态画成混合态，也不要让多个本应互斥的答案通过 Checkbox 造成可同时选择的预期。只读完成记录不需要因此变成可勾选控件。

## Similar & Easily Misused Components

- [Radio](radio.md) 表达同组至多一个选择；Checkbox 表达独立、可并列成立的选择。
- [Switch](switch.md) 控制功能开启或关闭；Checkbox 关注对象或条件是否被选中。
- [Selection Tree](selection-tree.md) 另有父节点覆盖后代的明确契约，不能把普通全选汇总规则直接套到树节点。

- [Guide Card](recommendation-panel.md) 的完成标记陈述事项已完成的事实；Checkbox 收集用户当前选择，不能把完成标记直接变成勾选入口。

## Composition

### Recommended

表格行 Checkbox 与 [Bulk Action Bar](bulk-action-bar.md) 分工：Checkbox 建立所选集合，批量操作区对集合执行动作。汇总 Checkbox 的作用范围应与可见说明及批量操作范围一致。

### Avoid

不要让整行点击执行导航时，同时无区分地切换 Checkbox；两个行为应有清晰目标。全选本页与全选全部结果不能共享模糊的“全选”语义。

## Internal Usage

Label 说明被选择的对象或条件。混合态只能由真实的部分选择关系支持。当前 state 会覆盖 checked/indeterminate，审查时应识别唯一状态来源，避免视觉选择与提交集合相互矛盾。

## Examples

### Recommended

文件表格逐行选择文件，表头说明“选择本页文件”，批量操作区展示选中数量。

### Problematic

把服务“正在连接”显示为半选 Checkbox，用户点击后既不能选择对象，也无法改变连接过程。
