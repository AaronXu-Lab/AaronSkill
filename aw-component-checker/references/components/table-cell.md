# Table Cell

Gallery ID: `table-cell`

## Definition & Semantics

Table Cell 表达某条记录在某一列中的值或局部交互，含义同时依赖所属行和列。当前组件渲染原生 td；content 类型区分展示组织，不会自动创建链接、选择控件或业务操作。

## When to Use

当信息属于表格记录的一个属性，或某一列专门承载行选择、行操作时使用。补充描述和尾部信息应继续解释同一个属性。

## When Not to Use

不要把 Table Cell 当成表格外的通用内容卡片。不要因 content="link" 就把普通文本视为可导航，也不要在一个单元格中堆入与列名无关的独立任务。

## Similar & Easily Misused Components

[Table Header](table-header.md) 定义列含义，Table Cell 提供该列的记录值。[Table Main Key](table-main-key.md) 专门组织行主标识及其入口。[Detail Field](detail-field.md) 自带标签和值，适合单个对象详情，不依赖公共列头。

## Composition

### Recommended

放在 [Table](table.md) 的记录行中，保持与列头对应。选择列组合 [Checkbox](checkbox.md)，操作列组合 [Action Button](action-button.md) 或 [Menu](menu.md)，由调用方将目标绑定到所属记录。

### Avoid

不要给一个 td 再套入本身已经输出 td 的 Table Main Key。避免在“状态”列同时放状态、全局新建和其他对象操作，使列职责失去一致性。

## Internal Usage

主值、前置图标、说明和尾部内容应指向同一字段。链接文本应识别其目的地；操作必须指向该行对象。表格内容类型只是容器声明，真正的交互语义由内部控件提供。

## Examples

### Recommended

“所有者”单元格显示用户名并链接到该所有者资料；补充说明为所属团队。

### Problematic

“文件大小”单元格显示大小，同时放置“创建工作区”按钮；按钮作用域超出了该字段和记录。
