# Tab Item

Gallery ID：`tab-item`。

## Definition & Semantics

Tab Item 是 [Tabs](tabs.md) 中一个同级内容区域的标签与选择入口。正式 API 为 Tabs.Item；单项依赖 Tabs 的共享选择关系，没有独立的页面导航系统。

## When to Use

当需要为 Tabs 中某个内容区域提供名称、可选图标和相关数量时使用。每项的值应与实际区域身份一致。

## When Not to Use

不要把 Tab Item 单独放在工具栏作为普通操作按钮，也不要靠手工选中样式模拟脱离 Tabs 的独立开关。没有对应内容区域的标签不构成有效 Tab Item。

## Similar & Easily Misused Components

- [Tabs](tabs.md) 管理整组及内容区域；Tab Item 只负责一个目的地的表示。
- [Button](button.md) 用于执行动作；Tab Item 用于显示某个区域。
- [Segmented](segmented.md) 的选项选择模式或参数，不要求各项对应 tabpanel。

## Composition

### Recommended

在同一个 Tabs.Root 和 Tabs.List 内组织同级 Tab Item，并为各项关联对应区域。组的统一设置由父级负责，避免单项擅自建立不同的导航层级。

### Avoid

不要在一个 Tab Item 的点击目标内嵌入删除、下载等独立按钮，让同一位置既切换章节又执行动作。章节操作应放入该区域明确的操作位。

## Internal Usage

Label 说明内容区域，icon 辅助识别同一区域，aux 表示该区域的数量。辅助数量不应描述另一个章节或当前选择之外的混合范围。当前实现的选中状态由父级值决定，不由单项另存一份状态。

## Examples

### Recommended

“附件 12”切换到附件区域，数量 12 指向该区域中的附件集合。

### Problematic

“下载 12”被做成 Tab Item，但点击后下载文件且不改变内容区域，标签实际表达的是操作。
