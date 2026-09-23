# Input

Gallery ID：`input`。

## Definition & Semantics

Input 接受一个字段的单行文本值。字段名称、当前值和辅助说明共同定义输入含义；输入行为本身不等同于搜索执行、导航或提交。

## When to Use

当字段内容应保持单行，用户需要自由输入或编辑名称、账号、关键词等值时使用。搜索框可用 Input 采集查询词，但搜索结果和选择规则由宿主负责。

## When Not to Use

不要把不能自由输入的有限选项伪装成文本框，也不要使用 Input 展示主要供长时间阅读的多段内容。一个输入框同时要求填写多个独立字段，会掩盖字段边界。

## Similar & Easily Misused Components

- [Input Area](input-area.md) 面向允许换行的文本；选择边界是内容结构，不是预估字符数。
- [Dropdown](dropdown.md) 从预定义值中选择，Input 允许编辑文本。
- [Composer](composer.md) 组织待发送内容及相关操作；一般表单字段不需要会话发送结构。

- [Detail Field](detail-field.md) 展示已知属性及相关操作；Input 收集或编辑值，不应仅为呈现字段边界而用于只读事实。

## Composition

### Recommended

输入字段可放入 [Dialog](dialog.md) 的紧凑任务正文，确认按钮负责提交。搜索 Input 与结果区域保持清楚关联；存在候选项选择时，需要另行定义完整的候选选择交互。

### Avoid

不要让清除当前字段的操作同时清空整个表单，也不要在字段尾部塞入与当前值无关的独立管理流程。字段自身有提交入口时，外部按钮不能以相同名称执行不同范围的提交。

## Internal Usage

Label 说明填写什么，当前值是用户数据，placeholder 仅作输入示例或提示。说明应解释该字段的约束或修正方式。前置图标与尾部操作均应服务当前字段，例如密码可见性；视觉必填标记不能替代实际必填约束。

## Examples

### Recommended

重命名 Dialog 中，Input 显示当前名称，用户编辑后由“重命名”确认新值。

### Problematic

“项目名称”字段尾部的齿轮打开全局账号设置，输入框与尾部操作不再表达同一个字段意图。
