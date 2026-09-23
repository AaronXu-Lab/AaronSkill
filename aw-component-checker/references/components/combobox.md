# Combobox

Gallery ID：`combobox`。

## Definition & Semantics

Combobox 表达从预定义集合中搜索并选择一个当前值。输入框中的临时文字用于过滤候选项，选中项才是字段提交的值；它不是允许任意自由文本的普通 Input。

## When to Use

当候选集合明确，但数量或辨识成本使逐项浏览低效，用户需要输入文字缩小范围后完成单值选择时使用。点击输入区域或尾部箭头均可打开与该字段关联的候选浮层。

## When Not to Use

短选项集合无需搜索时使用 [Dropdown](dropdown.md)。允许提交任意文本、创建集合外新值或只采集搜索词时使用 [Input](input.md) 并由宿主承担结果区域。动作集合不能因为带搜索就建模为 Combobox。

## Similar & Easily Misused Components

- [Dropdown](dropdown.md) 同样提交预定义单值，但触发器不可编辑；Combobox 的输入文字会过滤候选项。
- [Input](input.md) 接受自由文本；Combobox 只能从候选集合中确定提交值。
- [Menu](menu.md) 表达上下文动作；Combobox 浮层中的行是同一字段的候选值。
- [Radio](radio.md) 持续展示少量互斥值，适合直接比较；Combobox 将大量候选收起并支持过滤。

## Composition

### Recommended

将输入框、尾部箭头按钮和候选浮层视为同一个选择字段。Label 说明选择维度，description 解释字段约束；宿主通过受控或非受控值管理最终选择。

### Avoid

不要让尾部箭头执行与当前字段无关的动作，也不要让输入框与另一个候选列表分别维护不同选择。远程加载、分页和创建新值需要额外产品契约，不能由基础 Combobox 默认暗示。

## Internal Usage

输入区域负责文字编辑与过滤，点击激活时打开候选浮层。尾部 caret 使用独立按钮，只在按钮 hover 时同时改变图标颜色和按钮背景；点击后打开浮层并将焦点交给输入框，有现有文字时全选，便于直接替换查询。多选模式的已选项使用 `dismissible`、`light / primary` Badge，并与 Combobox 使用同名尺寸：`sm/md/lg` 对应 Badge `sm/md/lg`（24／28／32px），避免固定宽度控件过早换行；多选区保留上下各 4px padding，并让空状态与单枚 Badge 状态共享 38／42／46px 的稳定最小高度。无限行 [Content Group](content-group.md) 将全部已选项与搜索 input 放在同一换行流中，不隐藏可移除项；input 吸收末行剩余宽度并保留最小搜索宽度。Base UI 将删除行为组合进 Badge，并继续负责选择与键盘导航。选项 hover、高亮、禁用和选中勾选沿用 Dropdown 的候选行语言。

## Examples

### Recommended

“选择成员”Combobox 初始显示当前成员；点击字段后出现候选列表，输入姓名缩小结果，选择候选后字段提交对应成员值。

### Problematic

在“选择成员”Combobox 中输入任意邮箱后直接提交，即使该邮箱不属于候选集合；界面把集合选择错误地变成了自由创建。
