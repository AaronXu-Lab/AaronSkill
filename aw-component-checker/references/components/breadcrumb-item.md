# Breadcrumb Item

Gallery ID: `breadcrumb-item`

## Definition & Semantics

Breadcrumb Item 表达路径中的一个层级位置，通常是可返回的祖先或当前所在节点。节点名称承担位置识别；可交互时，调用方提供真实链接或按钮及其行为。

## When to Use

在 Breadcrumb 的祖先路径或当前节点位置使用。一个节点应代表一个可解释的层级，而不是一组无共同目的地的标签。

## When Not to Use

不要用 Breadcrumb Item 代替独立操作按钮或普通分类标签。clickable 只是组件呈现条件，不能代替真实目的地、动作或禁用逻辑。

## Similar & Easily Misused Components

[Breadcrumb](breadcrumb.md) 管理完整路径语义，Item 只表达其中一处位置。[Tab Item](tab-item.md) 表达同级内容目标。[Breadcrumb Separator](breadcrumb-separator.md) 没有目的地，不应赋予相同交互身份。

## Composition

### Recommended

放入 Breadcrumb，并在相邻节点间组合 Breadcrumb Separator。祖先导航用真实链接；当前节点可用静态文本；确实发生局部操作时才提供对应按钮，不能使用伪链接。

### Avoid

不要将多个节点都标记为当前位置。不要在一个节点中放多个互不相关的导航入口；current 或 clickable=false 不会自动移除调用方传入元素自身的点击能力，需要保证组合行为一致。

## Internal Usage

文字命名当前层级，图标或 Avatar 只辅助识别同一个目标。current 只标记实际当前位置；提供 render 后，元素类型和行为必须符合该节点的用途。

## Examples

### Recommended

项目资料的祖先节点渲染为真实链接，末尾合同名称是静态当前位置。

### Problematic

节点文字写“资源”，点击却删除当前资源；或者显示不可点击样式但仍保留活动链接。
