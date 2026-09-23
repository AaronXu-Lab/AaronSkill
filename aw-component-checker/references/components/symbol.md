# Symbol

Gallery ID: `symbol`

## Definition & Semantics

Symbol 是对象的辅助视觉标识。图标可以表达对象类别，图像可以表达对象自身；Symbol 不独立承担命名、操作或状态控制。

## When to Use

对象名称已经由相邻文本提供，同时需要帮助区分资源、组织或内容类别时使用。对象详情和对象候选项可以复用同一识别含义。

## When Not to Use

不要把 Symbol 当成无标签按钮、状态指示器或唯一的对象名称。当前 Symbol 默认对辅助技术隐藏，内部不能承载必须读取或操作的内容。

## Similar & Easily Misused Components

- [Avatar](avatar.md) 表示人员或参与者身份；Symbol 表示一般对象或类别。两者的外形相似不改变该边界。
- [Badge](badge.md) 补充状态或属性，Symbol 负责识别对象。失败图标如果是当前状态，应进入状态内容，而不是无条件替换对象标识。
- [Ask User Option Symbol](ask-user-option-symbol.md) 是回答选项的状态部件；Symbol 不表达答案是否被选中。

## Composition

### Recommended

在 [Detail Hero](detail-hero.md)、[Grid Item](grid-item.md) 或 [Menu Item](menu-item.md) 中将 Symbol 与同一对象的名称组合。操作交由所属条目或独立 [Button](button.md) 承担。

### Avoid

不要在同一对象入口中放入多个无解释的 Symbol，让用户误以为存在多个独立对象。不要在 Symbol 内嵌入链接或选择控件，造成标识与控制职责混合。

## Internal Usage

图标应对应对象类别，图像应对应对象本身；装饰性图形不能暗示不存在的身份、认证或完成状态。可读名称保留在 Symbol 之外。

## Examples

### Recommended

资源详情以 Symbol 显示文件类别图标，Detail Hero 标题显示具体资源名称。

### Problematic

把一个勾号放入 Symbol，并省略状态说明，要求用户自行推断对象是否已完成。
