# Content Group

Gallery ID: `content-group`

## Definition & Semantics

Content Group 汇集一组同类紧凑值，并在展示范围受限时保留集合的概览。收拢表示部分内容暂未展示，不表示过滤、分页或选择。

## When to Use

同一对象关联多个独立标签，用户首先需要概览，隐藏项只需查看时使用。当前正式内容契约面向 Badge；需要逐项操作时应重新评估是否适合收拢。

## When Not to Use

不要将主要操作、必读错误或必须逐项确认的选项收入隐藏集合。Content Group 不是任意复杂组件的容器，也不负责在服务器上加载更多记录。

## Similar & Easily Misused Components

- [Item Section Group](item-section-group.md) 组织完整条目，Content Group 组织紧凑值；判断依据是每项是否有独立内容和操作职责。
- [Filter Bar](filter-bar.md) 管理生效筛选条件，Content Group 只组织已有内容。
- [Tooltip](tooltip.md) 是当前隐藏值的展示依赖，不是集合管理器；Content Group 的 `+n` 不应被解读为打开操作菜单。

## Composition

### Recommended

在 [Table Cell](table-cell.md) 或对象摘要中组合只读 [Badge](badge.md)，让标签集合仍归属于一个字段。收拢计数用于表达还有多少未显示项。

### Avoid

当 `overflow="count"` 时，隐藏项进入 Tooltip，不要把可移除 Badge、按钮或输入控件作为需要在溢出区操作的子项。当 `overflow="hidden"` 时，超出范围的项没有查看入口，更不能将必要操作放入该集合。不要在同一集合外再放一套不一致的“更多”计数或分页控制。

## Internal Usage

子项应采用同一分类标准，避免混入进度、命令与无关状态。`+n` 表示未显示的子项数量，不能改作未读数。静默隐藏仅适合省略后不影响任务判断的补充信息；关键标签应在其他可持续读取的位置保留。`lines={0}` 表示无限行，不执行溢出收拢，也不创建隐藏测量副本；只有调用方明确承担全部交互可见性时，才可将其作为可移除 Badge 的纯排列容器。

## Examples

### Recommended

列表中的一个文档显示若干只读主题标签，其余标签通过 `+n` 查看。

### Problematic

把批量操作按钮放进 Content Group，窗口变窄后“删除”只存在于 Tooltip 内。
