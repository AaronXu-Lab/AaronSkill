# Dialog

Gallery ID：`dialog`。

## Definition & Semantics

Dialog 将当前上下文中的一次确认、简短说明或紧凑输入任务集中到模态表面。当前组件使用普通 Dialog 语义，并在 Dialog Basic 上提供说明、单行输入和自定义内容组合；破坏性外观不会自动变为 alertdialog。

## When to Use

当用户需要暂时聚焦一个边界明确的决定，并在完成或取消后返回原上下文时使用。内容应服务同一决定，而不是把一个完整页面缩进弹窗。

## When Not to Use

不需要决定的成功反馈不应阻断为 Dialog。需要长期驻留、独立访问的工作适合页面；需要边操作边参照背景内容的工作不适合当前模态壳。

## Similar & Easily Misused Components

- [Dialog Basic](dialog-basic.md) 提供同一任务等级的结构壳，不预设说明或输入正文；Dialog 提供常见正文组合。
- [Sheet Basic](modal-panel.md) 更适合浏览、搜索或管理对象的临时工作区，区别是任务结构而非仅有尺寸。
- [Alert](alert.md) 保留页面或对象信息；Dialog 要求临时转移任务焦点。
- [Menu](menu.md) 选择上下文动作，Dialog 可承接动作后的决定。

## Composition

### Recommended

普通主次操作通过 primaryAction 与 secondaryAction 配置，由 Dialog 统一组织。需要复杂的高级页脚时明确使用 customActions，并用 [Modal Actions](modal-actions.md) 保持主路径。紧凑选择任务可以组合 [Selection Tree](selection-tree.md)，由树管理暂选、确认操作提交。

### Avoid

避免在正文和底部各放一套同名确认按钮，或把选择候选项与最终提交写成无法区分的相同行为。Dialog Basic 不是绕过操作约束的替代入口；同一任务层级不应因为插槽方便而改变语义。

## Internal Usage

标题说明当前任务，说明解释决定所需信息，输入只采集该决定所需值。操作名称应说明实际后果。配置操作的异步完成、校验与关闭由调用方负责；界面关闭不等于操作成功。当前 child 明确选择正文组合，未传 child 的兼容组合不能被当作额外语义模式。

## Examples

### Recommended

重命名 Dialog 提供当前名称和“重命名”操作，取消保留原名，成功后再关闭。

### Problematic

点击“删除”后 Dialog 立即关闭并暗示成功，但后台失败时既没有保留决定上下文，也没有明确结果反馈。
