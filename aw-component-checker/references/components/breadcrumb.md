# Breadcrumb

Gallery ID: `breadcrumb`

## Definition & Semantics

Breadcrumb 以有序层级路径说明当前对象或页面位于哪里，并提供返回祖先上下文的入口。路径表达信息架构关系，不是用户访问历史或操作步骤。

## When to Use

当当前内容具有对用户有意义的上级关系，且返回某一级有助于定位时使用。路径应随实际位置更新，而不是随最近点击顺序拼接。

## When Not to Use

同级视图切换、连续填写步骤和浏览器后退历史不应伪装成层级路径。没有有意义的层级时，简单页面标题通常更直接。

## Similar & Easily Misused Components

[Tabs](tabs.md) 切换同级内容，Breadcrumb 表达祖先路径。[Sidebar Item](sidebar-item.md) 支持常驻导航和对象切换，Breadcrumb 补充当前路径。[Breadcrumb Item](breadcrumb-item.md) 是路径节点，[Breadcrumb Separator](breadcrumb-separator.md) 只表达节点间的层级连接。

## Composition

### Recommended

在 [Topbar](topbar.md) 等位置区域中组合 Breadcrumb Item 与 Breadcrumb Separator。需要同时显示 [Detail Hero](detail-hero.md) 时，路径负责祖先关系，Hero 负责当前对象的详细身份。

### Avoid

不要把同级分类排成父子路径，也不要将路径节点变为一组全局操作。隐藏最终节点仅适用于当前对象已由邻近标题清楚表达的组合，不能让用户失去当前位置。

## Internal Usage

各节点应按祖先到当前位置排列，名称应与实际目的地一致。当前实现 hideLastItem 会隐藏最后一个 Breadcrumb Item 并保留最后分隔符；这是祖先路径配合当前标题的组合能力，不能作为随意截断长路径的方式。

## Examples

### Recommended

“资源 / 项目资料 / 合同”表示当前合同所属目录，祖先节点返回相应范围。

### Problematic

用户依次访问“设置”“帮助”“报告”，界面把访问顺序串成 Breadcrumb，错误暗示报告属于帮助。
