# Sidebar Item

Gallery ID: `sidebar-item`

## Definition & Semantics

Sidebar Item 表达常驻侧栏中的一个导航入口或可切换对象，并可管理该入口的可折叠子项。active 表达当前上下文；open 表达子内容可见性，两者不等同于待提交的选择。

## When to Use

当用户需要在应用模块、对象或历史记录之间反复切换，且入口属于稳定侧栏结构时使用。入口可以只有主操作，也可以有清楚归属的子项。

## When Not to Use

普通设置行、临时命令列表或弹窗中的候选选择不应仅因呈现为一行就使用 Sidebar Item。不要通过 active 暗示完成状态或多选状态。

## Similar & Easily Misused Components

[Item](item.md) 是一般信息或设置行。[Selection Tree](selection-tree.md) 管理层级候选与选择模型。[Menu Item](menu-item.md) 属于临时上下文操作。[Sidebar Section Header](sidebar-section-header.md) 是集合标题，不是当前对象。

[Tabs](tabs.md) 组织当前工作区域的同级内容，[Breadcrumb](breadcrumb.md) 表达祖先路径；Sidebar Item 提供持久导航入口，当前项高亮不使三者成为同一种导航。

## Composition

### Recommended

使用 Sidebar Section Header 对入口按真实主题分组。通过 items 组织子入口，通过 [Sidebar Item Meta](sidebar-item-meta.md) 补充短状态，通过 [Menu](menu.md) 承载对象级次要操作。Sidebar Statements Scenario 的状态切换仅适用于同类会话条目。

### Avoid

不要让主操作、尾部菜单和展开状态分别指向不同对象。不要再用外部独立折叠器管理同一批 items，或让展开父项必然触发一个会立刻带离当前侧栏的无关导航。

## Internal Usage

标签命名目的地或对象；图标辅助识别。通知、加载和待处理信息应分别描述真实状态，不能将选中态当作通知。当前组件主入口是按钮语义，调用方负责实际导航，不应假定已具备原生链接的地址与新窗口能力。

## Examples

### Recommended

历史会话条目点击后打开对应会话；尾部菜单重命名同一会话，菜单操作不再触发行导航。

### Problematic

点击项目展开子项时又跳到无关设置页；active 高亮则随是否展开变化，而不是随当前上下文变化。
