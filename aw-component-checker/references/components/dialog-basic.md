# Dialog Basic

Gallery ID：`dialog-basic`。

## Definition & Semantics

Dialog Basic 提供标题、关闭入口、内容区域和操作区的模态结构。组件不预设任务正文；调用方决定正文内容，主次操作契约与 [Dialog](dialog.md) 相同。

## When to Use

当任务仍是一次明确决定或紧凑说明，但正文已有专门结构、不适合 Dialog 的预设组合时使用。需要明确标题和完整自定义正文即可成立，不要求更复杂的业务。

## When Not to Use

不要为了获得任意按钮布局就切换到 Dialog Basic。需要独立搜索、持续浏览和管理多个对象的工作区，不能仅靠自由 children 就视为紧凑 Dialog 任务。

## Similar & Easily Misused Components

- [Dialog](dialog.md) 在同一结构上增加常见正文组合；二者不是轻重两种模态语义。
- [Sheet Basic](modal-panel.md) 提供更完整的临时工作区结构。
- [Modal Actions](modal-actions.md) 只是操作区，不能独立提供模态上下文。

## Composition

### Recommended

自定义正文可以包含 [Tabs](tabs.md) 或紧凑表单，只要所有内容仍服务同一任务。使用结构化操作声明主路径；高级页脚通过 customActions 和 Modal Actions 明确组合。

### Avoid

避免在 children 中再次嵌入另一个完整弹窗壳来获得标题或按钮。任务已有一个主路径时，自定义正文不应另建脱离外层操作区的并行确认流程。

## Internal Usage

标题应准确命名自定义正文的共同任务。正文包含多个区块时，各区块仍应服务同一次决定。当前未配置操作时存在默认取消和确认入口；实际产品应明确其后果，不能把默认文案当作业务已经实现。

## Examples

### Recommended

“如何添加设备”展示两类设备的说明 Tabs，并提供一个“知道了”退出入口；所有内容解释同一任务。

### Problematic

用 Dialog Basic 包住完整设置中心，正文里每个章节有独立保存，外层又有含义不明的“确认”，产生两级提交范围。
