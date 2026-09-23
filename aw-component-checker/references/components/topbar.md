# Topbar

Gallery ID: `topbar`

## Definition & Semantics

Topbar 为页面、面板或模态工作区建立当前上下文，并组织作用于该上下文的入口。Topbar 提供内容与操作结构，导航、选择和关闭行为由调用方决定。

## When to Use

一个工作区域需要明确身份以及与该区域直接相关的操作时使用。主内容可以是标题、层级路径或同级内容切换，但应能够说明当前工作上下文。

## When Not to Use

不要把 Topbar 当作承载所有应用入口的杂项工具条。局部详情分区只需标题与少量操作时，应评估该分区的结构组件；对象的完整摘要也不应塞进顶栏。

## Similar & Easily Misused Components

- [Detail Hero](detail-hero.md) 描述对象身份、摘要和对象级内容，Topbar 建立工作区身份与控制入口；二者可以分工，但不应重复完整摘要。
- [Sidebar Header](sidebar-header.md) 面向导航容器的身份与控制，Topbar 面向当前工作区域。
- [Detail Section Header](section-header.md) 定义详情内部章节，不能被误当作第二层页面顶栏。
- [Breadcrumb](breadcrumb.md) 表达祖先路径，[Tabs](tabs.md) 表达同级内容；Topbar 可以承载这些组件，但不改变各自语义。

## Composition

### Recommended

在主内容中选用与信息架构匹配的标题、Breadcrumb 或 Tabs，尾部 [Button](button.md)、[Menu](menu.md) 和搜索只作用于该工作范围。Dialog Basic 和 Sheet Basic 已组合 Topbar，调用时沿用父组件的标题契约。

### Avoid

不要在同一范围同时呈现两组互相独立的 Tabs，或在已有父级顶栏的模态容器中再叠一个重复标题和关闭入口的 Topbar。局部搜索与全局搜索并存时必须区分范围。

## Internal Usage

标题、辅助 Badge 与尾部操作应指向同一上下文。下拉标题确实需要改变上下文或选择值时才使用；纯标题不应伪装成可点击控件。关闭是调用方提供的普通按钮，不能仅凭 X 图标假定关闭逻辑已经存在。

## Examples

### Recommended

文件工作区以 Breadcrumb 显示路径，尾部搜索限定当前集合，并提供该范围的新建操作。

### Problematic

顶栏标题是当前文件夹，旁边没有范围说明的搜索却查整个账户，同时出现另一组控制不同对象的同名 Tabs。
