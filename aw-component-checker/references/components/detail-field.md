# Detail Field

Gallery ID: `detail-field`

## Definition & Semantics

Detail Field 将一个属性标签与该属性的值配对，并可提供与该值直接相关的复制、操作或链接。核心职责是阅读已知事实，而非收集输入。

## When to Use

当用户查看单个对象的属性，需要明确知道值的含义时使用。复制标识、打开相关对象或编辑该属性可以作为辅助操作，但不改变主要阅读结构。

## When Not to Use

不要用 Detail Field 冒充可编辑输入框。需要横向比较多条记录时，Table 更合适；一段没有明确属性含义的说明也不应强拆成标签和值。

## Similar & Easily Misused Components

[Item](item.md) 围绕一条信息或设置意图组织控件，Detail Field 围绕属性和值。[Table Cell](table-cell.md) 依赖公共列头。[Input](input.md) 收集或编辑值，不是展示已知事实。[Detail Hero](detail-hero.md) 则确立对象整体身份。

## Composition

### Recommended

置于由 [Detail Section Header](section-header.md) 命名的属性分区。值可组合 [Badge](badge.md)；短选项可用 `type="dropdown"` 承载 [Dropdown Inline](dropdown-inline.md) 就地修改；辅助 [Action Button](action-button.md) 应作用于该属性。复制成功使用 Copy Button Feedback Scenario 的就地反馈。

### Avoid

不要在值后放与该属性无关的全局行动。不要同时配置两套含义相同但复制内容不同的复制入口；当前 copyText 会占用 hover 操作层，不应把该层同时设计为另一个必要入口。

## Internal Usage

标签解释“这是什么属性”，值回答该属性。copyText 应与用户认为正在复制的内容一致，必要时区分格式化展示与原始值。操作或链接标签应说明作用于哪个值；状态不能与未知、空值混用。`type="dropdown"` 时，value 应提供 Dropdown Inline；Detail Field 的 value 容器向起始侧补偿 6px，使透明静止态中的文字与 Label 对齐，而 hover 表面可以自然超出文字边缘。

## Examples

### Recommended

“运行编号”显示完整编号，并提供复制该编号的按钮，成功后在原按钮位置反馈；短枚举属性可用 `type="dropdown"` 显示始终可见的 Dropdown Inline。

### Problematic

“所有者”字段的尾部按钮实际删除整个对象，但界面只写“操作”，范围与属性不一致。
