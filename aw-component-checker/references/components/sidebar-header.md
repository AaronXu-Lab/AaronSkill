# Sidebar Header

Gallery ID: `sidebar-header`

## Definition & Semantics

Sidebar Header 锚定侧栏的身份或主要入口，并组织作用于整个侧栏上下文的操作。组件不负责给下方每个分组命名，也不提供完整导航树。

## When to Use

当应用存在常驻侧栏，需要稳定的品牌、返回入口、侧栏切换或全局入口时使用。入口含义应在侧栏展开和收起时保持一致。

## When Not to Use

不要把某个数据分区标题、对象摘要或页面详情头放在 Sidebar Header 中。仅有少量普通内容行时，不应为了使用这个组件建立一个伪侧栏。

## Similar & Easily Misused Components

[Sidebar Section Header](sidebar-section-header.md) 命名侧栏中的一组入口；Sidebar Header 锚定整个侧栏。[Topbar](topbar.md) 属于页面或工作区顶部结构，不自动承担侧栏身份职责。[Sidebar Item](sidebar-item.md) 是具体导航或对象入口。

## Composition

### Recommended

与 Sidebar Item 组成常驻导航，确需分组时加入 Sidebar Section Header。尾部可组合 [Menu](menu.md) 触发器承载侧栏级操作，操作范围应由应用上下文确定。

### Avoid

不要把只作用于当前页面某条记录的操作放到整个侧栏头部。避免 Sidebar Header 和 Topbar 同时提供含义与状态不同的两个“收起侧栏”入口。

## Internal Usage

前置品牌或图标应与入口作用一致；按钮名称不能只描述图形。当前 brand 形态仍是按钮，调用方应提供清楚的行为和名称；组件不会因传入 Logo 自动知道首页或返回路径。

## Examples

### Recommended

侧栏顶部的产品标识返回工作区入口，尾部按钮控制同一侧栏展开或收起。

### Problematic

侧栏头部显示当前文件名，并把删除当前文件放在产品标识旁，使对象级操作看似应用级操作。
