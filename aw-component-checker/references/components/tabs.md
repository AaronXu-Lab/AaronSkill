# Tabs

Gallery ID：`tabs`。

## Definition & Semantics

Tabs 组织同一工作上下文中的同级内容区域，一次展示当前选中的区域。Tabs 负责共享选择与结构，每个 [Tab Item](tab-item.md) 标识一个内容目的地。

## When to Use

当内容具有明确的同级章节，用户需要在这些章节之间切换，且每个标签都能对应清楚的内容区域时使用。

## When Not to Use

不要用 Tabs 表示必须依次完成的步骤、执行按钮组或整个应用的全局位置。仅修改排序、显示密度或其他参数时，不应为了外观采用章节导航语义。

## Similar & Easily Misused Components

- [Segmented](segmented.md) 改变同一内容的模式或参数；Tabs 切换有明确身份的同级内容区域。
- [Tab Item](tab-item.md) 是 Tabs 的单项，不能替代 Root/List/Panel 的整体关系。
- [Sidebar Item](sidebar-item.md) 可表达持久的应用导航入口；Tabs 主要服务当前工作上下文。
- [Breadcrumb](breadcrumb.md) 表达所在层级路径，[Pagination](pagination.md) 切换同一集合的数据页；Tabs 切换同级内容区域，不能把路径或分页伪装成章节。

## Composition

### Recommended

让 Tabs.List 中的 Tab Item 与对应内容区域保持一致。章节内可以使用 [Filter Bar](filter-bar.md) 收敛当前集合，或用 Segmented 改变展示模式；宿主明确这些状态是否跨章节保留。

### Avoid

避免另一组导航以相同标签控制同一内容却不同步选择。嵌套 Tabs 只有在子章节确有独立结构时才成立，不能把重复的同一分类再建立一层。

## Internal Usage

标签应描述内容而非待执行动作，选中状态应对应当前展示区域。Root 统一控制组内呈现；每项可以提供辅助数量，数量只能解释该章节，不能替代章节名称。

## Examples

### Recommended

详情页的“概览”“活动记录”对应两个内容区域，活动记录中的筛选只作用于记录集合。

### Problematic

用“填写信息”“确认”“完成”三个可自由跳转的 Tabs 包装必须按顺序验证的流程，标签的导航承诺与任务约束冲突。
