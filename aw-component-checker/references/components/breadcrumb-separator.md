# Breadcrumb Separator

Gallery ID: `breadcrumb-separator`

## Definition & Semantics

Breadcrumb Separator 表达相邻路径节点之间的层级连接，仅承担结构提示。组件没有导航、展开或选择职责。

## When to Use

在 Breadcrumb 的相邻层级节点之间使用。分隔符的存在必须有可解释的路径关系。

## When Not to Use

不要用分隔符作为返回按钮、展开箭头或下一步操作。普通文本中的标点和列表分隔不需要这个路径专用结构。

## Similar & Easily Misused Components

[Breadcrumb Item](breadcrumb-item.md) 表达位置且可以提供目的地，Separator 不代表位置。[Breadcrumb](breadcrumb.md) 才是完整路径；单独排列几个箭头不会形成导航结构。

## Composition

### Recommended

与 Breadcrumb Item 交替组合在 Breadcrumb 内。父组件使用 hideLastItem 并由邻近标题表达当前对象时，可以保留末尾分隔符作为指向当前内容的路径提示。

### Avoid

不要在普通完整路径的开头或末尾无故添加分隔符。不要把一个 separator 变成可点击按钮，使同一图形同时承担路径关系和操作。

## Internal Usage

分隔符不承载名称、数量或状态。caret 与 slash 都表示路径层级分隔，不能让同一路径中的符号切换暗示未定义的不同关系。

## Examples

### Recommended

“团队 / 项目 / 文件”用两个分隔符连接三层位置。

### Problematic

把路径中的右箭头绑定为“创建文件”，用户无法分辨符号是关系还是操作。
