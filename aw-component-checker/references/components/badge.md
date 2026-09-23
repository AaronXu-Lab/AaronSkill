# Badge

Gallery ID: `badge`

## Definition & Semantics

Badge 为明确对象标注简短的状态、分类或元信息。普通 Badge 是信息；可移除 Badge 表示能够撤销的一项标记或关联，移除行为不等于删除对象。

## When to Use

用户需要快速判断对象的一项属性，且短标签足以表达含义时使用。多个标签可以描述同一对象的不同属性，但每项属性应有明确来源。

## When Not to Use

不要用 Badge 代替独立操作、互斥选项或开关。需要说明失败影响与恢复步骤时，单个“失败”标签不足以承担反馈职责。

## Similar & Easily Misused Components

- [Filter Pill](filter-pill.md) 同样呈现紧凑条件，但代表对结果集合生效且可调整的筛选；Badge 通常只陈述对象属性，可移除并不自动构成筛选器。
- [Alert](alert.md) 解释需要持续关注的问题，Badge 只概括状态。
- [Sidebar Item Meta](sidebar-item-meta.md) 依赖侧栏条目的尾部信息语境，Badge 可用于一般对象的显式标记。
- [Avatar](avatar.md) 与 [Symbol](symbol.md) 识别主体，Badge 补充主体的属性。

## Composition

### Recommended

将 Badge 放在对应对象标题或 [Table Cell](table-cell.md) 中。多个只读分类可由 [Content Group](content-group.md) 收拢。存在处理步骤的失败可由 Badge 概括，并由同一对象范围内的 Alert 说明影响。

### Avoid

不要在同一属性上并列多个互斥状态而不说明不同时间或阶段。可移除 Badge 的整枚区域都是移除按钮，不要再嵌入另一项打开或编辑操作。

## Internal Usage

标签、图标与移除动作应指向同一属性。当前实现提供 `sm`、`md`、`lg`、`xl` 四档，整体高度依次为 24、28、32、36px；`sm/md` 使用 caption，`lg/xl` 使用 body-sm。仅在相应内容类型下渲染图标，提供 `icon` 不会自动切换成图文类型。移除名称应说明移除哪项标记，不能误导为删除所属对象。

## Examples

### Recommended

文档条目显示“只读”Badge；用户移除检索上下文标签时，仅移除该关联。

### Problematic

给“已启用”Badge 绑定启停功能，既没有开关语义，又使当前状态与可执行动作混在一起。
