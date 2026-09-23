# Dropdown

Gallery ID：`dropdown`。

## Definition & Semantics

Dropdown 表达从预定义集合中选择一个当前值。触发器应让用户识别字段及当前选择，浮层中的选项描述同一选择维度。当前正式 Gallery 以单值选择为语义基线。

## When to Use

当选项集合明确，用户不需要自由输入，并且无需持续并排比较全部选项时使用。选项可以附带简短说明，帮助用户区分同一维度的取值。

## When Not to Use

大量选项需要过滤搜索、用户需要自由创建值或需要复杂多选时，不应仅凭底层原语的潜在能力把普通 Dropdown 当作现成方案。普通操作集合也不应仅因采用浮层就建模为字段值。

## Similar & Easily Misused Components

- [Radio](radio.md) 持续展示互斥选项，便于比较；Dropdown 将同一选择集合收起。
- [Segmented](segmented.md) 适合少量且切换频繁的模式；Dropdown 更适合收起的值选择。
- [Menu](menu.md) 表达上下文动作，也可承接明确的菜单内单选；判断依据是触发器呈现字段值还是开放操作。
- [Input](input.md) 允许自由输入。
- [Selection Tree](selection-tree.md) 表达有父子关系的选择；Dropdown 的平面分组不能替代可展开的层级。

- [Button](button.md) 的分裂主体执行默认动作，箭头打开备选动作；Dropdown 的触发器呈现当前字段值，箭头外观不决定组件语义。
- [Filter Pill](filter-pill.md) 表示一个当前筛选条件并提供编辑或移除入口；Dropdown 负责选取值，不自行定义条件的生效与移除。
- [Dropdown Inline](dropdown-inline.md) 同样表达预定义单值选择，但固定为依附紧凑宿主的 24px rounded 触发器；Dropdown 继续承担完整字段、尺寸、宽度、标签、说明与校验状态。

## Composition

### Recommended

与其他表单字段共同表达一个任务时，Dropdown 保持独立字段身份。在 [Filter Bar](filter-bar.md) 之外单独使用时，宿主应让筛选范围与当前值清楚可见。

### Avoid

避免与另一个控件同时控制相同字段却不同步当前值。一般新设计不把删除对象混作普通选项；本项目“资源分享完整流程”是已存在的特定组合，权限值与分隔后的移除动作由调用方区别处理，不能把该例外扩展为任意字段菜单。

## Internal Usage

Label 说明选择维度，选项 Label 说明取值，description 只解释该选项。触发器自定义文字必须仍忠实表达当前值。危险选项的提示不代表组件会提供确认、执行删除或处理权限；这些后果由调用方明确承担。

## Examples

### Recommended

“显示语言”Dropdown 显示当前语言，展开后提供可选语言；选择后值与触发器保持一致。

### Problematic

“显示语言”下拉中混入“删除账号”，并在删除后把当前语言保存为“删除账号”；命令被错误建模为字段值。
