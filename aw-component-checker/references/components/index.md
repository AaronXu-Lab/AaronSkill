# Component References

本索引以当前 `gallery/gallery-registry.ts` 中 `NAV_GROUPS` 的 `general` 与 `composite` 为正式范围。Gallery 当前共 **89** 个正式 Panel：Foundations **40** 个、Composites **49** 个；本索引覆盖 **84** 个，对应 Reference 也为 **84** 份。既有 `ask-user-approval`、`guide-card-item`、`otp-input`、`strength-meter` 与 `toc` 尚未纳入索引与 Reference。Number Field 已移入 Temporary，因而不再收录。Bar Chart 与 Pie Chart 虽注册于 temporary section 源文件，仍属正式 Foundations；Suggestion 已迁入正式 UI 源码并直接注册于 Composites。Temporary、Styles、Rules、Scenarios 以及没有正式 Panel 的 provider、hook 和工具不收录。

按用户意图和所属区域识别组件，再使用 Gallery ID 匹配文件。仅加载当前涉及的规则；需要比较边界时再沿规则中的相对链接补读。当前名称与代码目录不必同名，例如 Guide Card 使用 `recommendation-panel.md`，Sheet Basic 使用 `modal-panel.md`，Detail Section Header 使用 `section-header.md`。

组件变更后的新增、移除、改名或分组同步使用 [编辑模式](../../docs/editing.md)；按最新正式注册维护表格与计数，当前数量不是固定目标。

## Terminology

| 术语 | 统一含义 |
| --- | --- |
| 操作 | 用户主动触发的一次行为，例如保存、打开或删除。 |
| 状态 | 对象或过程当前的事实；不等同于用户可以执行的动作。 |
| 选择 | 从对象或选项中确定目标或值；与执行后续操作分开判断。 |
| 导航 | 改变当前访问位置或内容范围，并保留明确的位置关系。 |
| 触发器 | 打开关联菜单、浮层或工作区的控制入口。 |
| 内容区域 | 围绕一个对象、集合或任务形成的界面范围。 |
| 模态 | 当前任务暂时限制对背景区域的交互；不表示所有浮层。 |
| 浮层 | 脱离普通内容流呈现的表面，是否模态由具体组件决定。 |
| 反馈 | 对操作进度、结果或需要关注的信息作出的表达。 |
| 职责 | 组件应负责的语义与行为边界，不等同于所占视觉区域。 |
| 调用方 | 为组件提供业务数据、状态和行为的使用方；“消费方”含义相同。 |
| 选中 / 当前 / 完成 | 分别表示选择结果、正在访问的位置与任务结束事实，不能混用。 |

## Foundations

| Gallery ID | 当前 Panel 名称 | Reference | 组件家族或主要关联组件 |
| --- | --- | --- | --- |
| `action-button` | Action Button | [action-button.md](action-button.md) | 操作 / Button |
| `avatar` | Avatar | [avatar.md](avatar.md) | 身份 / Symbol |
| `badge` | Badge | [badge.md](badge.md) | 状态与元信息 / Filter Pill |
| `button` | Button | [button.md](button.md) | 操作 / Action Button |
| `bar-chart` | Bar Chart | [bar-chart.md](bar-chart.md) | 数据图表 / Pie Chart |
| `pie-chart` | Pie Chart | [pie-chart.md](pie-chart.md) | 数据图表 / Bar Chart |
| `checkbox` | Checkbox | [checkbox.md](checkbox.md) | 选择 / Radio、Switch |
| `combobox` | Combobox | [combobox.md](combobox.md) | 可搜索选择 / Dropdown、Input |
| `content-group` | Content Group | [content-group.md](content-group.md) | 内容集合 / Badge |
| `dropdown` | Dropdown | [dropdown.md](dropdown.md) | 选择 / Radio、Menu |
| `dropdown-inline` | Dropdown Inline | [dropdown-inline.md](dropdown-inline.md) | 紧凑选择 / Dropdown、Action Button |
| `empty-state` | Empty State | [empty-state.md](empty-state.md) | 反馈 / Skeleton、Alert |
| `file-chip` | File Chip | [file-chip.md](file-chip.md) | 文件内容 / Composer Attachment |
| `input` | Input | [input.md](input.md) | 文本输入 / Input Area |
| `input-area` | Input Area | [input-area.md](input-area.md) | 文本输入 / Input |
| `item` | Item | [item.md](item.md) | Item 家族 |
| `item-section-group` | Item Section Group | [item-section-group.md](item-section-group.md) | Item 家族 |
| `item-surface` | Item Surface | [item-surface.md](item-surface.md) | Item 家族 |
| `lightbox` | Lightbox | [lightbox.md](lightbox.md) | 内容预览 / Message Media、File Chip |
| `menu` | Menu | [menu.md](menu.md) | Menu 家族 |
| `menu-header` | Menu Header | [menu-header.md](menu-header.md) | Menu 家族 |
| `menu-item` | Menu Item | [menu-item.md](menu-item.md) | Menu 家族 |
| `pagination` | Pagination | [pagination.md](pagination.md) | Pagination 家族 |
| `progress` | Progress | [progress.md](progress.md) | 等待与进度 / Spinner |
| `radio` | Radio | [radio.md](radio.md) | 选择 / Checkbox、Dropdown |
| `scrollbar` | Scrollbar | [scrollbar.md](scrollbar.md) | 内容位置 / Pagination |
| `segmented` | Segmented | [segmented.md](segmented.md) | 切换 / Tabs、Radio |
| `skeleton` | Skeleton | [skeleton.md](skeleton.md) | 内容占位 / Spinner、Empty State |
| `sonner` | Sonner | [sonner.md](sonner.md) | 事件反馈 / Alert |
| `spinner` | Spinner | [spinner.md](spinner.md) | 等待 / Progress、Skeleton |
| `switch` | Switch | [switch.md](switch.md) | 状态控制 / Checkbox |
| `symbol` | Symbol | [symbol.md](symbol.md) | 身份 / Avatar |
| `tabs` | Tabs | [tabs.md](tabs.md) | Tabs 家族 |
| `tab-item` | Tab Item | [tab-item.md](tab-item.md) | Tabs 家族 |
| `tooltip` | Tooltip | [tooltip.md](tooltip.md) | 辅助说明 / Menu、Sonner |
| `topbar` | Topbar | [topbar.md](topbar.md) | 工作区结构 / Detail Hero、Sidebar Header |
| `turn-navigator` | Turn Navigator | [turn-navigator.md](turn-navigator.md) | 会话导航 / Pagination |

## Composites

| Gallery ID | 当前 Panel 名称 | Reference | 组件家族或主要关联组件 |
| --- | --- | --- | --- |
| `alert` | Alert | [alert.md](alert.md) | 持续反馈 / Sonner |
| `ask-user` | Ask User | [ask-user.md](ask-user.md) | Ask User 家族 |
| `ask-user-option` | Ask User Option | [ask-user-option.md](ask-user-option.md) | Ask User 家族 |
| `ask-user-option-symbol` | Ask User Option Symbol | [ask-user-option-symbol.md](ask-user-option-symbol.md) | Ask User 家族 |
| `breadcrumb` | Breadcrumb | [breadcrumb.md](breadcrumb.md) | Breadcrumb 家族 |
| `breadcrumb-item` | Breadcrumb Item | [breadcrumb-item.md](breadcrumb-item.md) | Breadcrumb 家族 |
| `breadcrumb-separator` | Breadcrumb Separator | [breadcrumb-separator.md](breadcrumb-separator.md) | Breadcrumb 家族 |
| `bulk-action-bar` | Bulk Action Bar | [bulk-action-bar.md](bulk-action-bar.md) | 集合操作 / Table、Grid Item |
| `code-block` | Code Block | [code-block.md](code-block.md) | 代码内容 / Message Answer、Lightbox |
| `composer` | Composer | [composer.md](composer.md) | Composer 家族 |
| `composer-inline` | Composer Inline | [composer-inline.md](composer-inline.md) | Composer 家族 |
| `composer-context-bar` | Composer Context Bar | [composer-context-bar.md](composer-context-bar.md) | Composer 家族 |
| `composer-attachment` | Composer Attachment | [composer-attachment.md](composer-attachment.md) | Composer 家族 |
| `detail-hero` | Detail Hero | [detail-hero.md](detail-hero.md) | Detail 家族 |
| `detail-field` | Detail Field | [detail-field.md](detail-field.md) | Detail 家族 |
| `section-header` | Detail Section Header | [section-header.md](section-header.md) | Detail 家族 |
| `detail-activity-group` | Detail Activity Group | [detail-activity-group.md](detail-activity-group.md) | Detail 家族 |
| `detail-activity` | Detail Activity | [detail-activity.md](detail-activity.md) | Detail 家族 |
| `dialog` | Dialog | [dialog.md](dialog.md) | Dialog 家族 |
| `dialog-basic` | Dialog Basic | [dialog-basic.md](dialog-basic.md) | Dialog 家族 |
| `filter-bar` | Filter Bar | [filter-bar.md](filter-bar.md) | Filter 家族 |
| `filter-pill` | Filter Pill | [filter-pill.md](filter-pill.md) | Filter 家族 |
| `grid-item` | Grid Item | [grid-item.md](grid-item.md) | Grid Item 家族 |
| `grid-item-infos` | Grid Item Infos | [grid-item-infos.md](grid-item-infos.md) | Grid Item 家族 |
| `recommendation-panel` | Guide Card | [recommendation-panel.md](recommendation-panel.md) | 任务引导 / Progress、Item |
| `message-query` | Message Query | [message-query.md](message-query.md) | Message 家族 |
| `message-answer` | Message Answer | [message-answer.md](message-answer.md) | Message 家族 |
| `message-footer` | Message Footer | [message-footer.md](message-footer.md) | Message 家族 |
| `message-activity` | Message Activity | [message-activity.md](message-activity.md) | Message 家族 |
| `message-job-card` | Message Job Card | [message-job-card.md](message-job-card.md) | Message 家族 |
| `message-media` | Message Media | [message-media.md](message-media.md) | Message 家族 |
| `modal-actions` | Modal Actions | [modal-actions.md](modal-actions.md) | 模态操作 / Dialog、Sheet Basic |
| `modal-panel` | Sheet Basic | [modal-panel.md](modal-panel.md) | 模态工作区 / Dialog Basic |
| `session-end` | Session End | [session-end.md](session-end.md) | 会话边界 / Composer |
| `session-info` | Session Info | [session-info.md](session-info.md) | 会话摘要 / Sidebar Item Meta |
| `suggestion` | Suggestion | [suggestion.md](suggestion.md) | 建议操作 / Button |
| `sidebar-header` | Sidebar Header | [sidebar-header.md](sidebar-header.md) | Sidebar 家族 |
| `sidebar-item` | Sidebar Item | [sidebar-item.md](sidebar-item.md) | Sidebar 家族 |
| `sidebar-section-header` | Sidebar Section Header | [sidebar-section-header.md](sidebar-section-header.md) | Sidebar 家族 |
| `sidebar-item-meta` | Sidebar Item Meta | [sidebar-item-meta.md](sidebar-item-meta.md) | Sidebar 家族 |
| `table` | Table | [table.md](table.md) | Table 家族 |
| `table-header` | Table Header | [table-header.md](table-header.md) | Table 家族 |
| `table-cell` | Table Cell | [table-cell.md](table-cell.md) | Table 家族 |
| `table-main-key` | Table Main Key | [table-main-key.md](table-main-key.md) | Table 家族 |
| `table-main-key-badge` | Table Main Key Badge | [table-main-key-badge.md](table-main-key-badge.md) | Table 家族 |
| `selection-tree` | Selection Tree | [selection-tree.md](selection-tree.md) | Tree 家族 |
| `selection-tree-item` | Selection Tree Item | [selection-tree-item.md](selection-tree-item.md) | Tree 家族 |
