# Sidebar Section Header

Gallery ID: `sidebar-section-header`

## Definition & Semantics

Sidebar Section Header 命名并组织侧栏中的一组入口，可选择控制该组内容展开或收起。分组标题表达共同范围，不代表其中一个具体目的地。

## When to Use

当侧栏入口有清楚的语义分组，且命名能帮助快速寻找时使用。只有存在所属内容且确实需要收起时，才启用折叠。

## When Not to Use

少量同类入口无需为形式完整而分组。不要把一个可直接打开的具体对象伪装成分区标题，也不要用侧栏分区头组织页面正文。

## Similar & Easily Misused Components

[Sidebar Header](sidebar-header.md) 锚定整个侧栏；[Sidebar Item](sidebar-item.md) 表达具体入口或对象。[Detail Section Header](section-header.md) 组织页面内容区域，虽然同样可以折叠，信息架构位置不同。

## Composition

### Recommended

在 content 中组合属于同一范围的 Sidebar Item。尾部 [Action Button](action-button.md) 或 [Menu](menu.md) 应操作该分组，例如在该组中新建对象。

### Avoid

不要让分组标题点击同时切换导航位置与无关选择。不要在分组外再维护一套相同内容的折叠状态，使标题的展开指示与实际内容不一致。

## Internal Usage

标题说明分组对象或范围；尾部计数应对应这组内容，操作名称应说明作用。当前需要显式 collapsible、实际 content 和配对的展开状态才能形成可折叠分组。

## Examples

### Recommended

“项目”分区包含项目入口，标题收起这些入口，右侧新建按钮只创建项目。

### Problematic

名为“收藏”的分区实际收起整个侧栏，右侧数字却是所有未读消息数。
