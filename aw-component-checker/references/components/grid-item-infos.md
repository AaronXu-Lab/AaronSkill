# Grid Item Infos

Gallery ID: `grid-item-infos`

## Definition & Semantics

Grid Item Infos 组织一个 Grid Item 的主标题和辅助身份信息，使用户先判断对象是谁，再理解来源或限定信息。组件本身不提供导航、选择或操作。

## When to Use

当 Grid Item 需要稳定的标题、副标题和紧凑辅助信息结构时使用。每段内容应帮助识别同一个对象。

## When Not to Use

不要用辅助身份区承载一组操作或长篇说明。详情页顶层对象标题与卡片内部标题不同，不应仅因字重相似就互相替换。

## Similar & Easily Misused Components

[Grid Item](grid-item.md) 承担完整对象结构，Grid Item Infos 只承担其中的身份区。[Table Main Key](table-main-key.md) 属于表格主列并带前置操作。[Detail Hero](detail-hero.md) 确立详情页顶层身份和主操作，层级不同。

## Composition

### Recommended

放入 Grid Item 的 infos 槽；对象摘要放在 Grid Item 内容区域，操作放在相应尾部区域。主标题与外层导航或选择目标保持同一个对象。

### Avoid

不要在 infos 中再次嵌入一张 Grid Item 或另一个详情页标题。避免标题旁、下方和 footer 反复显示同一状态，而没有不同判断用途。

## Internal Usage

标题识别对象；副标题补充来源、归属或必要限定。辅助文本与辅助图标必须表达同一个属性，不能一个表示更新时间、另一个却表示权限。

## Examples

### Recommended

项目卡片以项目名为标题、所属团队为副标题，并用辅助文本标明来源。

### Problematic

主标题写“最近更新”，真正对象名放在辅助文本里，使用户无法先识别卡片对象。
