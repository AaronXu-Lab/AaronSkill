# Component Reference Evidence Index

本文件是研究阶段的临时证据索引，可以整体删除。正式运行入口、工作流和 Component References 不引用本文件；删除后不影响规则理解、相对链接或按需加载。

核对日期：2026-09-12。正式范围来自当前 `gallery/gallery-registry.ts` 中 `NAV_GROUPS` 的 `general` 与 `composite`，共 80 个 Panel（34 个 Foundations、46 个 Composites）。本地路径默认相对于 axo-design-system 仓库根目录；各 ADM 条目中的 `app-design-mock/...` 和未写仓库前缀的产品路径均属于只读的 `../axo-app-fe`。行号仅用于本次研究定位，后续变更应以组件及实现名称重新定位。

证据用于支持语义判断，不为历史实现背书。公开实现、类型和当前行为与较早 Gallery 说明或交接记录冲突时，已记录采用当前能力的依据。没有无法通过调查与合理判断解决的核心语义问题，因此不创建空的 `_unresolved.md`。

## 操作、输入、选择与浮层：研究记录

本节是可删除的研究记录，不属于正式运行时规则。所有 ADM 路径都经过只读检查；读取前核对了 ADM 根目录 AGENTS.md、AGENTS.design.md，Git user 为 XuWeinan123。公共背景为 ADM `DESIGN.md:522` 起的 Components、`src/components/ui/CONVENTIONS.md`，正式范围来自当前 `gallery/gallery-registry.ts` general + composite。以下 Scenario 只用于核对语义及组合；尺寸、间距、颜色和通用键盘检查没有扩写进正式 References。

### action-button — Action Button

- 本地：`src/components/ui/ActionButton/index.tsx`、`types.ts`；`gallery/sections/controls.tsx:67` ActionButtonDemo 与 `:130` 注册；`HANDOFF.md` 2026-09-11 Action Button content types。确认 text/icon/iconText 均为宿主内部操作，hoverIcon 只替换图标。
- ADM：`app-design-mock/src/components/files/upload-queue/index.tsx:233`–262，逐条上传的失败重试与队列取消；证明局部对象操作真实存在，不把具体状态实现当作推荐规范。
- Scenario：`gallery/scenarios/actions.tsx` 的 Actions' Gap；`gallery/scenarios/resource-sharing.tsx:286` CopyButtonFeedbackScenario。前者仅明确操作集合所属关系，后者支持原位置反馈；没有把间距表写入本 Skill。
- 外部：[WAI-ARIA APG Button](https://www.w3.org/WAI/ARIA/apg/patterns/button/) 支持操作与链接、状态的区分，以及名称应识别动作。

### button — Button

- 本地：`src/components/ui/Button/index.tsx`；`gallery/sections/controls.tsx:95`–156 的 ButtonSample、ButtonDefaultContent 与注册；`docs/buttons-adoption-audit.md`。核对原生 button、独立 split 主体/箭头和 Menu 结构，不能把 split 当成 Select。
- ADM：`app-design-mock/src/pages/auth/login/components/email-password-login-form/form.tsx:77`–130 的字段与提交；`pages/projects/detail/prompt-section.tsx:54` 起保存、取消草稿。实际主次动作范围可区分，不继承其中的样式作为语义标准。
- Scenario：`gallery/scenarios/buttons.tsx`，特别是同一任务主路径、分裂按钮视为一项、不同任务分组；`resource-sharing.tsx:286` 原位复制反馈。
- 外部：[WAI-ARIA APG Button](https://www.w3.org/WAI/ARIA/apg/patterns/button/) 支持主动动作、导航边界及开关按钮的独立状态语义。

### input — Input

- 本地：`src/components/ui/Input/index.tsx`；`gallery/sections/controls.tsx:158`–189；`gallery/gallery-demos.tsx:86` DialogDemo；`docs/dialog-actions-migration.md` 的表单与提交约定。核对输入字段与尾部 slot，不虚构候选选择器。
- ADM：`app-design-mock/src/pages/auth/login/components/email-password-login-form/form.tsx:77`–130，邮箱、密码和密码可见性；`views/project-rename-dialog/index.tsx`，受控名称与原生表单提交。
- Scenario：`gallery/sections/scenarios.tsx:183` RenameDialogScenario 与其 DialogDemo 实现；`gallery/scenarios/resource-sharing.tsx:460` 输入搜索组合，候选过滤和选择由调用方承担。
- 外部：[MDN input](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input)、[MDN textarea](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/textarea) 支持单行与多行内容边界；[Base UI Select](https://base-ui.com/react/components/select) 支持预定义选值与可搜索输入不能混同。

### input-area — Input Area

- 本地：公开导出 `src/components/ui/index.ts:274` 指向 `src/components/ui/TextArea/index.tsx`；`gallery/sections/controls.tsx:191`–215。核对原生 textarea 和当前 editable/readOnly 都使 canEdit=false、tabIndex=-1、聚焦后 blur 的特殊行为。
- ADM：`app-design-mock/src/pages/projects/detail/prompt-section.tsx`，多行 Prompt 草稿及保存，纯阅读时改为 p；只用于证明阅读与编辑确有不同任务。
- Scenario：当前注册表没有专门针对一般多行字段的语义 Scenario；Buttons' Gap 只适用于其外部保存动作组。没有凭借未读的 Composer 细节推导输入行为。
- 外部：[MDN textarea](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/textarea) 支持多行纯文本输入定义。当前只读焦点行为与一般原生 textarea 能力有差异，Reference 明确区分实现事实与阅读任务，不承诺原生只读交互。

### dropdown — Dropdown

- 本地：`src/components/ui/Dropdown/index.tsx`；`gallery/sections/controls.tsx:42` DropdownExample、`:217` 注册；`src/components/ui/CONVENTIONS.md` 字段与状态约定。当前以 Gallery 单值选择为语义基线，未把 Base UI 新版本潜在多选能力写成当前公开能力。
- ADM：`app-design-mock/src/components/resource-share-dialog/collaborators.tsx:155`–183，权限值与独立 remove 分支。
- Scenario：`gallery/sections/scenarios.tsx` FloatingSurfacesSamples/DropdownSurfacePreview；`gallery/scenarios/resource-sharing.tsx:252` 协作者权限下拉混入 remove、`:577` 邀请权限单值选择。Reference 保留前者为当前明确范围内的组合，不把其做法推广到所有字段，也不无依据禁止既有 Scenario。
- 外部：[Base UI Select](https://base-ui.com/react/components/select) 的定义和 Usage guidelines：选择预定义值，长列表需要过滤时考虑 Combobox；[WAI-ARIA APG Radio](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) 支持与持续可见互斥答案的边界。

### checkbox — Checkbox

- 本地：`src/components/ui/Checkbox/index.tsx`；`gallery/sections/controls.tsx:241`–255。核对 state 最终覆盖 checked/indeterminate，不把展示态当作业务集合已经更新。
- ADM：`app-design-mock/src/pages/design/files/components/file-table/row.tsx:112`–118，逐行文件选择与 TableCell。
- Scenario：当前注册的 File & Folder Picker/Multiple Entry Select 没有直接给普通 Checkbox 提供新的混合态规则；Selection Tree 的特殊组选择规则不能据此反向覆盖普通 Checkbox。未加入无依据的场景规则。
- 外部：[WAI-ARIA APG Checkbox](https://www.w3.org/WAI/ARIA/apg/patterns/checkbox/)、[Switch](https://www.w3.org/WAI/ARIA/apg/patterns/switch/) 支持部分选择汇总、可并列选择与功能开关的区别。

### radio — Radio

- 本地：`src/components/ui/Radio/index.tsx`；`gallery/sections/controls.tsx:257`–273，Gallery 使用 BaseRadioGroup 包住 Radio。核对单项与组的关系，不虚构库导出 RadioGroup。
- ADM：针对 `app-design-mock/src/**/*.tsx` 搜索直接 `<Radio\b` 没有找到已验证实例；现有 RadioOptions 是其他组件，不能当作本 Panel 的直接使用证据。背景仅采纳 `DESIGN.md:608` Selection Controls 的选择意图。
- Scenario：当前注册表无专门 Radio Scenario。
- 外部：[WAI-ARIA APG Radio Group](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) 支持同组至多一项、可以初始未选及组问题/选项答案的关系。

### switch — Switch

- 本地：`src/components/ui/Switch/index.tsx`；`gallery/sections/controls.tsx:275`–285。仅封装 BaseSwitch，不拥有业务状态持久化。
- ADM：`app-design-mock/src/pages/me/settings/index.tsx:46`–74 及其对应 Item，控制工具和显示偏好；只用于证明主动开关功能，不将调试业务带入规则。
- Scenario：无独立开关 Scenario。Buttons' Gap 明确 Switch 与按钮的混合结构不等于普通操作按钮组。
- 外部：[WAI-ARIA APG Switch](https://www.w3.org/WAI/ARIA/apg/patterns/switch/) 支持二值开关、名称不随状态改变、与 Checkbox 的语义选择。即时生效是场景建议，Reference 对统一保存场景附有明确条件，没有冒充 APG 硬约束。

### segmented — Segmented

- 本地：`src/components/ui/Segmented/index.tsx`；`gallery/sections/controls.tsx:287`–309。核对 ToggleGroup、默认首项、忽略空选择以及不创建 tabpanel。
- ADM：`app-design-mock/src/pages/design/jobs/list/index.tsx:149`–157 的布局切换；`pages/me/settings/index.tsx:30`–43 的外观偏好、`:78`–96 的速度设置。
- Scenario：`gallery/scenarios/buttons.tsx` 中尺寸与内容形式选择，证明 Segmented 选择参数而非执行命令；没有将示例选项作为业务规则。
- 外部：[WAI-ARIA APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)、[Radio Group](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) 用于区分内容区域导航与互斥答案；始终保留一个值来自当前实现。

### tabs — Tabs

- 本地：`src/components/ui/Tabs/index.tsx` 全部 Root/List/Item/Panel 及类型；`gallery/sections/controls.tsx:311`–325；`docs/components-content-migration.md` “用户确认保留 Tab 组内统一设置”记录。父组拥有统一设置。
- ADM：`app-design-mock/src/pages/design/workers/home/index.tsx:325` 起完整 Tabs.List/Tabs.Panel，设备说明同级区域；`pages/design/jobs/list/index.tsx:120`–157，与 FilterBar/Segmented 并用的真实范围关系。后者缺少直接 Panel 的实现没有被包装为正式标准。
- Scenario：无专用 Tabs 语义 Scenario；Buttons' Gap 文档明确 Tabs/Segmented 不按普通动作组处理。
- 外部：[WAI-ARIA APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) 支持标签与内容区域映射，Reference 不从可见标签外观推断导航契约成立。

### tab-item — Tab Item

- 本地：`src/components/ui/Tabs/index.tsx` ItemProps/Item；`gallery/sections/controls.tsx:327`–351，TabItemGalleryFrame 内仍包含 Tabs.Root/List；`docs/components-content-migration.md` 已确认组内设置归父级。
- ADM：`app-design-mock/src/pages/design/jobs/list/index.tsx:129`–134 的 aux 数量；`pages/design/workers/home/index.tsx:334` 起区域对应关系。
- Scenario：无专门单项 Scenario；不将 Gallery 孤立展示当作组件可以脱离 Tabs 使用的依据。
- 外部：[WAI-ARIA APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) 支持每个 tab 标识一个 panel；数量和统一外观归属来自本地实现。

### menu — Menu

- 本地：`src/components/ui/Menu/index.tsx`、MenuGroup、MenuGroupLabel、MenuRadioGroup、MenuRadioItem；`gallery/sections/overlays.tsx:181`–198 与 `:328` 注册；`CONVENTIONS.md` 非空分组分隔线规则。
- ADM：`app-design-mock/src/pages/design/skills/components/skill-list-item-grid/index.tsx:80`–130 的对象菜单；`components/layout/index.tsx:285`–304 的真实 RadioGroup 来源选择。条件分隔线等历史风险仅供识别，不照抄为推荐。
- Scenario：`gallery/sections/scenarios.tsx` Floating Surfaces、SidebarStatementsScenario；`gallery/scenarios/resource-sharing.tsx:460`–547 搜索输入与菜单结果的特定组合，调用方显式控制输入、结果和邀请。
- 外部：[WAI-ARIA APG Menu Button](https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/)、[Menu and Menubar](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/)、[Base UI Select](https://base-ui.com/react/components/select) 支持动作菜单、菜单单选及字段选值的界线。没有把所有 Menu 一概限制为无状态命令。

### menu-header — Menu Header

- 本地：`src/components/ui/MenuHeader/index.tsx`、`Menu/MenuGroupLabel.tsx`；`gallery/sections/overlays.tsx:162` MenuHeaderPreview 与 `:338` 注册。展示 div 与原语组标签具有不同职责。
- ADM：`app-design-mock/src/components/layout/index.tsx:289`–300，Menu.RadioGroup 内的“按来源筛选”组标题；不是独立 MenuHeader 导出调用。
- Scenario：Floating Surfaces/MenuPreview 中分组结构；ResourceSharing Dropdown 分组可复用显示型 MenuHeader，但选择语义仍归 Select。
- 外部：[WAI-ARIA APG Menu and Menubar](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/) 支持分组、非操作分隔元素和单选组关系。MenuHeader 本身的非交互定义由本地实现及 Gallery 明确。

### menu-item — Menu Item

- 本地：`src/components/ui/MenuItem/index.tsx`、`Menu/MenuRadioItem.tsx`；`gallery/sections/overlays.tsx:168` MenuItemPreview 和 `:354` 注册。核对普通 BaseMenu.Item 的尾部 Check 只呈现图标，RadioItem 才由原语管理选中。
- ADM：`app-design-mock/src/views/side-bars/main/user-profile/index.tsx:86`–104 的身份和操作条目；`pages/design/skills/components/skill-list-item-grid/index.tsx:88` 起对象动作。退出登录的 destructive 历史值未当作通用规则。
- Scenario：Resource Sharing 的 avatar/symbol 搜索结果条目与邀请任务；Floating Surfaces 的 MenuPreview。
- 外部：[WAI-ARIA APG Menu and Menubar](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/) 支持 menuitem 与 menuitemradio 的状态区别；内部内容只表达一项意图是本地 API 与任务语义的综合判断。

### tooltip — Tooltip

- 本地：`src/components/ui/Tooltip/index.tsx`；`gallery/sections/overlays.tsx:370` 注册与真实悬停 Demo；`gallery/gallery-demos.tsx:327` TooltipPreview；`docs/release-0.19.0.md` 已取消 Arrow 的记录。
- ADM：`app-design-mock/src/pages/design/workers/components/worker-version-tag/index.tsx:44`–65，“版本过低”辅助解释。该使用中关键信息是否足够常驻需要按上下文判断，没有把历史 href="#" 或阻断说明当作推荐。
- Scenario：`gallery/sections/scenarios.tsx` Floating Surfaces。Content Group 隐藏内容的交互边界与负责该家族的 agent 交叉核对，正式 Reference 禁止把必须操作的内容仅藏入提示。
- 外部：[Base UI Tooltip](https://base-ui.com/react/components/tooltip)；[WAI-ARIA APG Tooltip](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) 支持目标说明与无可聚焦子控件边界。APG 页面注明仍是未达共识的工作稿，因此不将其单独包装为最终规范。

### dialog — Dialog

- 本地：`src/components/ui/Dialog/index.tsx`、`DialogBasic/index.tsx`、`DialogBasic/actionTypes.ts`；`gallery/sections/overlays.tsx:218`–238；`gallery/gallery-demos.tsx:86`–178；`docs/dialog-actions-migration.md`。以当前 actionTypes 为准，不沿用旧文档的 ReactNode actions。
- ADM：`app-design-mock/src/views/project-rename-dialog/index.tsx`，名称草稿、原生提交、校验与异步成功后关闭；证明确认与编辑是同一边界明确的任务。
- Scenario：Rename、File & Folder Picker；Resource Sharing 中邀请确认；Floating Surfaces。确认选择和改变暂选是不同职责。
- 外部：[WAI-ARIA APG Modal Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) 支持背景不可交互的模态语义，以及普通 dialog 与 alertdialog 的区别。未把项目默认主操作焦点视为所有高风险决定的普遍推荐。

### dialog-basic — Dialog Basic

- 本地：`src/components/ui/DialogBasic/index.tsx`、`actionTypes.ts`；`gallery/sections/overlays.tsx:240`–258；`gallery/gallery-demos.tsx:86`–178、`:206` DialogPreview；`docs/dialog-actions-migration.md`。Basic 仍有相同操作约束，不是自由操作后门。
- ADM：`app-design-mock/src/pages/design/workers/home/index.tsx:325` 起，自定义设备说明正文及同一“知道了”任务出口。
- Scenario：Floating Surfaces，Rename 的共用对话框结构；没有为了 Basic 单独制造一套任务级别。
- 外部：[WAI-ARIA APG Modal Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) 支持模态任务边界。Basic 与 Dialog 的区别由项目实现确定，外部资料不赋予不存在的独立语义。

### modal-panel — Sheet Basic

- 本地：`src/components/ui/SheetBasic/index.tsx` 与公开类型；`gallery/sections/overlays.tsx:87`–159 的真实/静态 SheetBasic Demo、`:260` 注册；`docs/release-0.19.0.md` Topbar 迁移记录。当前名称以 Sheet Basic 为准，ID 保留 modal-panel。
- ADM：`app-design-mock/src/pages/session/composer/file-space-picker-dialog.tsx` 的多选文件工作区；集合、加载状态、重试和确认均在相同任务上下文中。
- Scenario：`gallery/sections/scenarios.tsx:80` MultipleEntrySelectScenario；`gallery/scenarios/resource-sharing.tsx:154` 批量邀请及 `:430` 分享工作区；Floating Surfaces。支持临时工作区、范围搜索和集中确认的职责。
- 外部：[WAI-ARIA APG Modal Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) 支持模态期间背景不可交互。Dialog/Modal 的工作区层级差异采用当前实现、Scenario 与 ADM DESIGN.md:674 的一致判断，未称为 ARIA 两种角色。

### modal-actions — Modal Actions

- 本地：`src/components/ui/ModalActions/index.tsx`；`gallery/sections/overlays.tsx:283`–305；`DialogBasic/actionTypes.ts`；`docs/dialog-actions-migration.md`。检查默认按钮没有业务回调、primary 标记、aux action/text 与主次分组。
- ADM：`app-design-mock/src/pages/session/composer/file-space-picker-dialog.tsx:67`–88，确认当前所选集合和取消；范围由调用方提供。
- Scenario：Buttons' Gap；Multiple Entry Select；Resource Sharing 的完成和辅助复制。只写分组语义，不展开具体间距或数量上限。
- 外部：[WAI-ARIA APG Modal Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) 与 [Button](https://www.w3.org/WAI/ARIA/apg/patterns/button/) 支持“模态任务中的操作”判断；槽位数量与 aux 行为来自本地实现。

### filter-bar — Filter Bar

- 本地：`src/components/ui/FilterBar/index.tsx` 全部类型与 pending/active 逻辑；`gallery/sections/composites.tsx:39`–89 的条件 Demo、`:614` 注册；`docs/components-content-migration.md:139`–143。核对 single 元组约束、每维度单值与未选值不提交。
- ADM：`app-design-mock/src/pages/design/jobs/list/index.tsx:120`–157，Tabs + FilterBar + Segmented；用于发现章节、条件、展示方式可以共存，不直接承认所有实现细节正确。
- Scenario：无独立筛选 Scenario；其 Menu 内部单选核对了当前 Menu.RadioGroup/RadioItem，Buttons' Gap 明确筛选项不属于普通操作按钮组。
- 外部：[WAI-ARIA APG Menu and Menubar](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/) 支持菜单内单选结构。筛选收敛结果、不修改对象的定义来自本地实现和 ADM DESIGN.md:718，不由菜单外观推断。

### filter-pill — Filter Pill

- 本地：`src/components/ui/FilterPill/index.tsx`；`gallery/sections/controls.tsx:353` 注册；FilterBar 的 Menu.Trigger/render 组合。确认修改与移除为两个按钮，disabled 只透传主按钮，未把不存在的全组件冻结能力写入规则。
- ADM：搜索 `app-design-mock/src/**/*.tsx` 未找到直接 `<FilterPill\b` 调用；`pages/design/jobs/list/index.tsx:138` 消费 FilterBar，胶囊经当前库内部组合出现。此处明确为间接使用。
- Scenario：无独立 Filter Pill Scenario；普通按钮分组规则不扩展为筛选胶囊内部行为。
- 外部：[Base UI Select](https://base-ui.com/react/components/select) 与 [WAI-ARIA APG Menu and Menubar](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/) 支持“编辑一个条件值”与“操作入口”的区分；胶囊与 Badge 的边界由当前 Panel 定义和 FilterBar 数据契约决定。

### 已通过证据解决的差异

- `docs/dialog-actions-migration.md` 的旧 ReactNode `actions`、`assistAction` 示例落后于当前 `actionTypes.ts`、ModalActions。正式规则使用结构化主次操作、高级 customActions 和当前 aux 概念；没有修改源文档或实现。
- Resource Sharing 的 Dropdown 移除条目是当前 Scenario 中有明确动作分支的特例。Reference 保留该范围条件，新的一般值字段不因此获得任意命令混用许可。
- Resource Sharing 的 Input + Menu 搜索不是库已封装好的 Combobox。Reference 区分具体调用方维护的搜索/选择协议与普通 Menu，避免将 Scenario 误推为自动支持。
- Input Area 的 readOnly 与原生 textarea 可聚焦阅读习惯存在实际差异。Reference 说明当前边界，并建议将明确阅读任务交给展示内容；该事实不改变组件的多行字段核心语义。
- Tabs/Tab Item 的组内设置曾出现在历史待决记录中，后续记录已确认父级统一设置，当前实现与最新说明一致，因此无须重新请用户确认。

本家族没有尚需产品确认才能决定核心语义的未决事项；没有创建空的 unresolved 文件。

## 结构、数据与导航 References 的研究证据

以下是研究阶段临时记录；不是运行时规则依赖。ADM 仅证明场景存在，其当前用法不自动构成推荐。研究前已读取 ADM 的 `AGENTS.md` 与 `AGENTS.design.md`；Git user 为 `XuWeinan123`，符合其只读调查条件。

共同本地依据：`src/components/ui/CONVENTIONS.md`；`src/components/ui/index.ts` 的公开导出；当前 `gallery/gallery-registry.ts` 正式 Panel inventory。ADM 背景为 `../axo-app-fe/DESIGN.md` 的 Sidebar、Detail Page、Setting Rows、Components / Toolbar & Breadcrumb、Selection Controls、Tables & Lists、Pagination。以下 Scenario 均已读取注册与被引用实现；这里只提炼语义，不扩展为视觉或键盘审计。

### table

- 本地：`src/components/ui/Table/index.tsx` 的 ITableProps、Table、TableHeader、TableHead、TableCell；`gallery/sections/composites.tsx:583` 及 TableComposedDemo；`gallery/sections/data.tsx` 的全部表格子项示例；`docs/table-scroll-area.md`。支持原生表格结构与消费者数据行为的边界。文档中的 TableBody / TableRow 旧示例不作为现行导出，正文依据当前实现使用原生 tbody / tr。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/files/components/file-table/index.tsx:75` 及 `row.tsx:122`，查看了列选择、全选、数据行、主名称与对象操作的具体组合。文件固定排序证明并非所有列都应可排序；其业务规则不推广到通用 Table。
- Scenario：没有表格专属语义 Scenario；组合局部操作时参考 `gallery/scenarios/actions.tsx`、`gallery/scenarios/buttons.tsx`，尺寸与间距不写入本 Reference。
- 官方：[APG Table](https://www.w3.org/WAI/ARIA/apg/patterns/table/)、[Carbon Data table](https://carbondesignsystem.com/components/data-table/usage/)。支持行列结构、内部控件与完整交互 grid / 工作表的区别；未把 Carbon 的扩展能力宣称为本地 API。

### table-header

- 本地：`src/components/ui/Table/index.tsx` 的 ITableHeadProps、TableHeader、TableHead；`gallery/sections/data.tsx:403` 与 TableHeaderDefaultDemo / ContentDemo / SortableDemo / SortDirectionDemo；`gallery/sections/composites.tsx` 的 TableComposedDemo。Panel 名称指列头职责，实际包含 thead 与 th 两层，不能把 TableHeader 误认为排序按钮。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/files/components/file-table/index.tsx:75`，已读全选范围、部分选中和各列名称的实现。
- Scenario：无直接适用的列头语义 Scenario。
- 官方：[APG Table](https://www.w3.org/WAI/ARIA/apg/patterns/table/)。支持列头解释数据、排序状态对应实际排序；全选范围规则来自本地消费者状态边界。

### table-cell

- 本地：`src/components/ui/Table/index.tsx` 的 ITableCellProps / TableCell；`gallery/sections/data.tsx:499` 及全部 TableCell*Demo；`gallery/gallery-demos.tsx:351` 的 TableCellActionButton。确认 content 类型不会自动创建内部控件。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/files/components/file-table/row.tsx:122` 起的选择、位置、相关资源、时间及操作单元，已读其实际组合。
- Scenario：操作组合涉及 Buttons' Gap；已读 `gallery/scenarios/buttons.tsx`，本 Reference 仅审查作用域，不复述尺寸。
- 官方：[APG Table](https://www.w3.org/WAI/ARIA/apg/patterns/table/)。支持具体记录值与列含义的关联，以及单元格容器和内部控件的区分。

### table-main-key

- 本地：`src/components/ui/TableMainKey/index.tsx` 的 ITableMainKeyProps 及组件；`src/components/ui/Table/index.tsx`；`gallery/sections/data.tsx:447` 与三个 TableMainKey*Demo。确认组件直接输出 td，leadingButtonProps 必须提供回调，名称不是自动链接。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/files/components/file-table/row.tsx:127`，已读前置展开 / 预览入口和名称详情入口的区别。文件业务的特殊图标与样式不作为通用规范。
- Scenario：Actions' Gap 适用于相关局部操作组合，`gallery/scenarios/actions.tsx` 已读；没有单独主标识语义 Scenario。
- 官方：[APG Table](https://www.w3.org/WAI/ARIA/apg/patterns/table/)。支持表格单元与内部操作分工；必需前置行为来自本地类型，而非外部规范。

### table-main-key-badge

- 本地：`src/components/ui/TableMainKeyBadge/index.tsx`；`src/components/ui/TableMainKey/index.tsx`；`gallery/sections/data.tsx:483`、TableMainKeyBadgeDemo 与 `gallery/sections/composites.tsx` 的 TableComposedDemo。支持依附行标识的类别标记，确认没有自带交互。
- ADM：对 `../axo-app-fe/app-design-mock/src/**` 做直接 JSX / 名称检索，未核验到 TableMainKeyBadge 的独立产品实例；已读 file-table/row.tsx 的通用 Badge 补充来源场景，二者不混记。
- Scenario：无直接适用的类别标记语义 Scenario。
- 官方：[Carbon Data table](https://carbondesignsystem.com/components/data-table/usage/) 只补充表格内容和行对象上下文；本组件的类别职责以本地说明和实现为主，没有从外部臆造交互能力。

### selection-tree

- 本地：`src/components/ui/SelectionTree/index.tsx`、`types.ts`、`selection.ts`、`SelectionTreeNodeItem.tsx`、`SelectionTreeItem.tsx`；`gallery/sections/data.tsx:361` 与 SelectionTreeModeDemo。确认 none / single / multiple、动态分组范围、逐项选择不自动上卷、取消组时展开一级选择结果。
- ADM：`../axo-app-fe/app-design-mock/src/pages/session/composer/file-space-picker-dialog.tsx:110`，已读调用方加载状态、草稿选择、明确确认和 groupSelectable=false 的实际组合；不把其按钮命名或旧 ModalActions API 当成规范。
- Scenario：`gallery/sections/scenarios.tsx` 的 FileFolderPickerScenario 与 DetailPageStructureScenario 已读；前者分开暂存选择与确认，后者示范 selectMode=none 的文件目录。
- 官方：[APG Tree View](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)。支持层级、展开和选择的区别；动态组范围及取消组规则为本地明确契约，并非所有树的通则。

### selection-tree-item

- 本地：`src/components/ui/SelectionTree/SelectionTreeItem.tsx` 的 ISelectionTreeItemProps；`SelectionTreeNodeItem.tsx` 的行为绑定；`gallery/sections/data.tsx:380` 与 SelectionTreeItemPreview。支持行展示与完整树行为的区别。
- ADM：未核验到独立 SelectionTreeItem 的产品实例；已读 `../axo-app-fe/app-design-mock/src/pages/session/composer/file-space-picker-dialog.tsx:110` 的 SelectionTree，行由库内部间接生成。
- Scenario：File & Folder Picker 与 Detail Page Structure 经 SelectionTree 间接适用，已读其实现；没有独立行专属 Scenario。
- 官方：[APG Tree View](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)。支持由树组织节点关系与统一选择模型，未将单独视觉行写为完整树。

### item

- 本地：`src/components/ui/Item/types.ts`、`index.tsx`、`ItemSectionGroup.tsx`；`gallery/sections/content.tsx:166` 的完整示例及 ItemGalleryFrame。确认 Item 本身是 div，尾部控件需要实际状态和行为。
- ADM：`../axo-app-fe/app-design-mock/src/pages/me/design-preferences/index.tsx:85` 起，已读主题与语言各用一行和受控 Segmented；另已读 referenced-job-detail.tsx 的产物信息行。仅用于证明设置行和信息行场景均存在。
- Scenario：DetailPageStructureScenario 的触发条目与 ItemSectionGroup；Buttons' Gap 的局部操作边界，均已读。
- 官方：[GOV.UK Summary list](https://design-system.service.gov.uk/components/summary-list/) 用于校对信息 / 属性和值的边界，不将该组件等同于 Item；Item 与设置控件的关系由本地实现和 ADM 上下文确定。

### item-section-group

- 本地：`src/components/ui/Item/ItemSectionGroup.tsx`；`gallery/sections/content.tsx:191` 的三个完整分组示例；`docs/temporary-component-cleanup.md` 确认本组件保留。
- ADM：`../axo-app-fe/app-design-mock/src/pages/me/design-preferences/index.tsx:85` 与 `pages/design/jobs/detail/referenced-job-detail.tsx:208`，已读成组设置和成组产物内容。
- Scenario：DetailPageStructureScenario 的触发详情分组，支持主题分组而非自动选择或事件链。
- 官方：[GOV.UK Summary list](https://design-system.service.gov.uk/components/summary-list/) 用于比较成组事实与事件历史；具体组结构和无状态能力以本地实现为准。

### grid-item

- 本地：`src/components/ui/GridItem/index.tsx`、`GridItemInfos.tsx`、`GridItemTrailing.tsx`；`gallery/sections/composites.tsx:679` 及 GridItemDemo / GridItemMenuButton / GridItemStage。确认 card/list 不改变对象语义，整卡交互与选择由外层承担。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/automations/components/automation-list-item-grid/index.tsx:111`，已读同一对象的标题、触发信息、recent、Switch / Run 与菜单组合。未把其设置名称当作标准文案。
- Scenario：`gallery/sections/scenarios.tsx` 的 MultipleEntrySelectScenario 已完整读取，选择和确认由 Modal 调用方管理；Buttons' Gap 只作局部组合背景。
- 官方：[Carbon Data table](https://carbondesignsystem.com/components/data-table/usage/) 用于 Table 与对象卡片的比较边界；选择能力从本地 Scenario 推导，没有写成 GridItem 内置 API。

### grid-item-infos

- 本地：`src/components/ui/GridItem/GridItemInfos.tsx` 的 IGridItemInfosProps；`GridItem/index.tsx`；`gallery/sections/composites.tsx:699` 及 GRID_ITEM_DEMO_PROPS。支持标题区与外层对象结构的分工。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/automations/components/automation-list-item-grid/index.tsx:121`，已读对象名与触发方式辅助信息；产品实例不作为所有卡片必须带触发字段的依据。
- Scenario：MultipleEntrySelectScenario 的 infos 只识别候选对象；父级实现已读。
- 官方：[Carbon Data table](https://carbondesignsystem.com/components/data-table/usage/) 仅用于父级结构差异；本子组件没有外部同名标准，规则主要来自当前实现和父级职责。

### detail-hero

- 本地：`src/components/ui/DetailHero/index.tsx`；`gallery/sections/composites.tsx:627` 与 DetailHeroDemo；`src/components/detail-page/DetailSection.tsx` 用于确认后续分区归属。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/jobs/detail/referenced-job-detail.tsx:115`，已读对象身份、上方 Alert、后续属性和历史结构；`DESIGN.md:359` 说明可省略重复 Hero。
- Scenario：DetailPageStructureScenario 已读，确认对象级 Alert → Hero → 内容分区的职责，不把具体状态优先级扩大为所有对象通则。
- 官方：[GOV.UK Summary list](https://design-system.service.gov.uk/components/summary-list/) 用于区分对象总览与具体事实；Hero 的对象级主身份与主操作由本地组件定义。

### detail-field

- 本地：`src/components/ui/DetailField/index.tsx`；`gallery/sections/navigation.tsx:185` 与 DetailFieldDemo；`docs/prompts/detail-field-consumer-migration.md` 的当前命名映射。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/jobs/detail/referenced-job-detail.tsx:139` 起已读运行时间、成本、来源、编号等属性；历史迁移名称不保留为正式 Reference API。
- Scenario：DetailPageStructureScenario；`gallery/scenarios/resource-sharing.tsx:286` 的 CopyButtonFeedbackScenario 已读，确认复制同一个值与成功就地反馈。
- 官方：[GOV.UK Summary list](https://design-system.service.gov.uk/components/summary-list/) 支持标签、已知事实及局部操作的边界；不将其 HTML dl 结构宣称为当前 DetailField 的 DOM。

### section-header

- 本地：`src/components/ui/SectionHeader/index.tsx` 的 IDetailSectionHeaderProps / DetailSectionHeader；`src/components/detail-page/DetailSection.tsx`；`gallery/sections/navigation.tsx:168` 与 DetailSectionHeaderDemo；`docs/component-redesign-handoff.md` 的分区头变更背景。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/jobs/detail/referenced-job-detail.tsx:224` 的 DetailSection，通过 headerProps 折叠执行过程；已经读取库内 DetailSection 对 DetailSectionHeader 的调用，属于已核验间接实例。
- Scenario：DetailPageStructureScenario，已读各分区及其内容。支持分区命名 / 折叠而非导航。
- 官方：[APG Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) 用于展开和状态切换边界；未扩展成一般键盘审计。

### detail-activity-group

- 本地：`src/components/ui/DetailActivity/DetailActivityGroup.tsx`；`gallery/sections/composites.tsx:663` 与 DetailActivityGroupDemo；`DetailActivity/index.tsx`。确认组不排序、不获取数据、不推导因果。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/jobs/detail/referenced-job-detail.tsx:231`，已读 job.events 映射与事件时间。
- Scenario：DetailPageStructureScenario 的最近运行记录；已读其事件内容和排列。
- 官方：[GOV.UK Summary list](https://design-system.service.gov.uk/components/summary-list/) 仅用于区分静态属性分组；事件连续性以本地组件说明为主，无外部通用因果假设。

### detail-activity

- 本地：`src/components/ui/DetailActivity/index.tsx` 的当前 / 兼容信息字段及标题、说明、时间呈现；`gallery/sections/composites.tsx:645` 与 DetailActivityDemo。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/jobs/detail/referenced-job-detail.tsx:233`，已读单次事件状态与内容对应关系。
- Scenario：DetailPageStructureScenario 的单次运行历史，已读。支持事件级结果与对象级状态不混同。
- 官方：[GOV.UK Summary list](https://design-system.service.gov.uk/components/summary-list/) 作为静态属性反例背景；本组件事件定义来自当前实现，不向其添加自动详情折叠。

### sidebar-header

- 本地：`src/components/ui/SidebarHeader/index.tsx` 的 ISidebarHeaderProps；`gallery/sections/navigation.tsx:126` 的完整示例，确认 brand 仍为 Button 且不拥有路由。
- ADM：`../axo-app-fe/app-design-mock/src/components/layout/index.tsx:271`，已读品牌、侧栏收起及筛选菜单组合；`DESIGN.md:349` 提供 Sidebar 所属层级背景。
- Scenario：无直接 Sidebar Header 语义 Scenario；Buttons' Gap 已读，只用于组合背景。
- 官方：[Carbon UI shell left panel](https://carbondesignsystem.com/components/UI-shell-left-panel/usage/) 支持常驻产品导航上下文；未照搬 Carbon 的层级数与项目数量限制。

### sidebar-item

- 本地：`src/components/ui/SidebarItem/index.tsx` 的 ISidebarItemProps、内部主操作和 Collapsible；`gallery/sections/navigation.tsx:245` 与 SidebarItemDemo；`docs/sidebar-internalization.md`，确认当前父组件统一拥有主操作及 items。
- ADM：`../axo-app-fe/app-design-mock/src/views/side-bars/main/history/session/index.tsx:106`，已读 active、待确认 / loading / unread 状态、导航回调与对象菜单。该产品实现不是通用状态优先级标准。
- Scenario：SidebarStatementsScenario 已读，对同类会话提供待处理和 selected 显示映射；Actions' Gap 已读。Reference 明确不将会话状态映射推广到所有对象。
- 官方：[Carbon UI shell left panel](https://carbondesignsystem.com/components/UI-shell-left-panel/usage/)、[APG Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/)，用于常驻导航与展开的职责区别。当前组件是按钮主入口，不写成链接实现。

### sidebar-section-header

- 本地：`src/components/ui/SidebarSectionHeader/index.tsx` 的状态契约；`gallery/sections/navigation.tsx:148` 与 SidebarSectionHeaderDemo，已读静态和受控折叠两种完整组合。
- ADM：`../axo-app-fe/app-design-mock/src/views/side-bars/main/history/index.tsx` 的项目与会话两组 SidebarSectionHeader，已读 content、expanded 和新建操作的实际范围。
- Scenario：无专属分组语义 Scenario；Actions' Gap 已读，Sidebar Statements 仅适用于其子条目。
- 官方：[Carbon UI shell left panel](https://carbondesignsystem.com/components/UI-shell-left-panel/usage/)、[APG Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/)。支持命名分组、子内容可见性与导航入口的区别。

### sidebar-item-meta

- 本地：`src/components/ui/SidebarItemMeta/index.tsx` 及 CSS；`src/components/ui/SidebarItem/index.tsx` 的 default / hover trailing；`gallery/sections/navigation.tsx:229`。Gallery 文字使用“hover surface”，但实际公开组件是行内 span，规则依据实现写为紧凑信息，由父级控制显示。
- ADM：未发现独立 JSX 调用；已读 `../axo-app-fe/app-design-mock/src/views/side-bars/main/history/session/index.tsx:106` 的 trailing="meta"，并核验库内 SidebarItem 调用，因此记录为间接实例。
- Scenario：SidebarStatementsScenario 已读，证明 Meta 可在常驻态显示，不是独立浮层能力。
- 官方：[Carbon UI shell left panel](https://carbondesignsystem.com/components/UI-shell-left-panel/usage/) 仅用于侧栏上下文；行内结构与显隐边界由本地证据解决，无需产品确认。

### breadcrumb

- 本地：`src/components/ui/Breadcrumb/index.tsx`；`BreadcrumbItem.tsx`、`BreadcrumbSeparator.tsx`；`gallery/sections/navigation.tsx:72`。确认 hideLastItem 保留末尾分隔符，长路径不由组件折成省略号。
- ADM：`../axo-app-fe/app-design-mock/src/components/toolbar/page-breadcrumb.tsx:11` 已读真实 Link、current 和 hideLastItem 组合；referenced-job-detail.tsx 的页面标题提供当前位置上下文。ADM 将“无 path”也视为 current 的写法未泛化为规范。
- Scenario：无直接 Breadcrumb Scenario。
- 官方：[APG Breadcrumb](https://www.w3.org/WAI/ARIA/apg/patterns/breadcrumb/)，支持祖先层级路径与当前位置的边界。hideLastItem 属于本地组合能力，不作为所有路径的通例。

### breadcrumb-item

- 本地：`src/components/ui/Breadcrumb/BreadcrumbItem.tsx` 的 render/current/clickable 组合；`gallery/sections/navigation.tsx:93`。确认 clickable/current 不会自行删除调用方元素已有行为。
- ADM：`../axo-app-fe/app-design-mock/src/components/toolbar/page-breadcrumb.tsx:19`，已读 router Link 与末项静态文本。
- Scenario：无直接节点语义 Scenario。
- 官方：[APG Breadcrumb](https://www.w3.org/WAI/ARIA/apg/patterns/breadcrumb/)。支持祖先目的地与当前位置；实际链接与按钮选择还遵循本地 CONVENTIONS 的 Inline links。

### breadcrumb-separator

- 本地：`src/components/ui/Breadcrumb/BreadcrumbSeparator.tsx`；`Breadcrumb/index.tsx` 的 hideLastItem；`gallery/sections/navigation.tsx:113`。确认装饰性结构，不含触发器。
- ADM：`../axo-app-fe/app-design-mock/src/components/toolbar/page-breadcrumb.tsx:18`，已读仅在相邻项之间插入的实现。
- Scenario：无直接适用 Scenario。
- 官方：[APG Breadcrumb](https://www.w3.org/WAI/ARIA/apg/patterns/breadcrumb/) 用于完整路径背景；分隔符非交互和本地末尾特例由当前源码决定。

### pagination

- 本地：`src/components/ui/Pagination/index.tsx` 的 PaginationProps 及早退规则；`gallery/sections/navigation.tsx:271` 与 PaginationDemo；`docs/temporary-component-cleanup.md:17`。确认现行只提供 range / simple 的相邻页，已移除数字页码子组件。
- ADM：检索 `../axo-app-fe/app-design-mock/src/**`，未核验到当前 Pagination 的直接产品实例；`../axo-app-fe/DESIGN.md:628` 描述分页需求，但其“页码模式”不视为当前库能力。
- Scenario：无直接分页语义 Scenario；不将 Buttons' Gap 扩写成分页规则。
- 官方：[GOV.UK Pagination](https://design-system.service.gov.uk/components/pagination/) 支持在能改善集合浏览时分成数据页。未照搬该系统的数字跳页和其他实现能力。

### bulk-action-bar

- 本地：`src/components/ui/BulkActionBar/index.tsx` 的 BulkActionBarProps、回调条件渲染、溢出 Menu；`gallery/sections/composites.tsx:563`，确认组件不管理集合，也不自动隐藏 count=0。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/files/list/index.tsx:606` 起已读多选替换 Tabs、计数、取消与外接批量快捷方式操作。该处没有为多个内置操作提供回调，不能用显示标签推定功能存在。
- Scenario：Buttons' Gap 的按钮层级与动作分组说明已读，Reference 不记录视觉数值。
- 官方：[Carbon Data table / Batch actions](https://carbondesignsystem.com/components/data-table/usage/)。支持对当前选择集合操作以及区分单项与批量目标；Carbon 对行操作的全面禁用建议在此提炼为发生作用域混淆时才隐藏、禁用或清楚区分，避免无条件推广。

### 已调查并解决的来源差异

- Sidebar Item Meta 的 Gallery “hover surface”不意味着独立浮层；源码和 Sidebar Statements 已解决，正式规则按行内信息编写。
- ADM DESIGN 的数字分页与旧 Table / Sidebar 文档中的已移除导出，仅作为历史背景；现行 Reference 以当前公开实现为准。
- Selection Tree 的动态分组选择比通常 Checkbox 聚合选择更具体；当前 registry 和 selection.ts 一致，因此保留为本地契约，不需要另行询问。
- 没有因这些差异留下待产品确认的核心语义问题。未修改 ADM、组件实现或 Gallery。

## 反馈、内容、身份与图表：研究记录

共同证据：本仓库 `AGENTS.md`、完整 `HANDOFF.md`、`src/components/ui/CONVENTIONS.md`、`src/components/ui/index.ts` 与 `src/index.ts` 的公开导出、当前 registry 的正式 Panel 归属。ADM 读取前已核对根 `AGENTS.md` 与 `AGENTS.design.md`，Git user 为 XuWeinan123；只读使用 `../axo-app-fe/DESIGN.md:522` 起的 Components 作为背景。以下产品位置证明场景存在，不能独自证明用法正确。当前实现与较早交接描述冲突时以实际公开类型和行为为准。

### avatar — Avatar

- 本地：`src/components/ui/Avatar/index.tsx`、`gallery/sections/content.tsx:111` 与 DebugAvatar、`docs/component-contract-update.md`、`docs/components-content-migration.md`。支持人员身份、缺少 src 的默认图；源码没有自动 onError 替换，故未承诺错误 fallback。
- ADM：`../axo-app-fe/app-design-mock/src/components/resource-share-dialog/collaborators.tsx:108` 起，人员 Avatar 与部门 / 成员组 Symbol 分支。
- Scenario：`gallery/scenarios/resource-sharing.tsx:105` PrincipalMarker 与 CollaboratorList；支持人物身份与非人物类别的区分。没有把 Temporary Identity Row 收入正式清单。
- 外部：该组件边界已由本地实现、Gallery 和 Scenario 交叉确定，无额外外部能力假设。

### symbol — Symbol

- 本地：`src/components/ui/Symbol/index.tsx`、`gallery/sections/content.tsx:90`；支持图标 / 图像标识与默认 aria-hidden。可操作内容不应嵌在辅助标识中。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/connectors/detail/overview-section/index.tsx`、`components/resource-share-dialog/collaborators.tsx:122` 起，分别核对对象和组织标识。
- Scenario：Resource Sharing 的 PrincipalMarker、`gallery/sections/scenarios.tsx` 的 DetailPageStructureScenario / DetailHero。支持标识、名称、状态各自分工。
- 外部：未用外部组件扩展本地 Symbol 的能力。

### badge — Badge

- 本地：`src/components/ui/Badge/index.tsx`、`gallery/sections/content.tsx:128`、`docs/components-content-migration.md`。静态 span 与整枚可移除 button 为不同契约；图标只随相应内容类型渲染。
- ADM：`../axo-app-fe/app-design-mock/src/pages/session/jobs-panel/job-status-badge.tsx`、`pages/design/workflows/editor/composer/WFComposer.tsx:164`。前者只传 icon 未指定图文类型，证明不能把历史调用作为正确图标渲染的依据；后者证明移除上下文关联的场景。
- Scenario：DetailPageStructureScenario 的状态 Badge 与详情信息分工；SidebarStatementsScenario 的尾部状态范围。未引入状态颜色规则。
- 外部：核心标记及移除行为均由本地实现支持，无新增能力假设。

### content-group — Content Group

- 本地：`src/components/ui/ContentGroup/index.tsx`、`gallery/sections/content.tsx:47` ContentGroupDemo 与 `:148` 注册。读取了隐藏测量、可见切片和 Tooltip 组合；count 将隐藏项放进 Tooltip，hidden 则直接省略，lines=0 不限制行。
- ADM：在 `../axo-app-fe/app-design-mock/src/**/*.tsx` 搜索直接 ContentGroup 调用，未核验到实例。只采用 DESIGN.md 的 Badge 分类背景，不虚构产品落点。
- Scenario：当前 registry 没有专门 Content Group 语义 Scenario；Floating Surfaces 的 Tooltip 只补充说明性质。
- 外部：与 [APG Tooltip](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) 的非交互说明边界交叉核对，由控件研究批次读取；由此限制 count 模式收拢可操作子项。该限制是当前组合推导，不是所有溢出容器的普遍禁令。

### file-chip — File Chip

- 本地：`src/components/ui/FileChip/index.tsx`、`gallery/sections/content.tsx:251`、`docs/component-contract-update.md` 与 HANDOFF 中 File Chip 的后续缺省修正。默认可点击、可选独立下载，具体打开 / 下载行为由调用方提供。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/workflows/components/job-summary-dialog/index.tsx:37` 的产物与证据文件采用静态形式；不把该复杂历史 Dialog 组合当作整体推荐案例。
- Scenario：没有 File Chip 专属 Scenario；CopyButtonFeedbackScenario 只支持发起控件就地反馈原则，不扩写为下载规则。
- 外部：未推断自动预览、上传或下载引擎；本地公开契约足以确定边界。

### alert — Alert

- 本地：`src/components/ui/Alert/index.tsx`、`gallery/sections/feedback.tsx:43`。组件为流内持续反馈，默认 role=alert 可由原生 props 覆盖，leading/trailing 不替调用方产生业务行为。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/workflows/components/job-summary-dialog/index.tsx:35` 起，部分结果与失败原因；DESIGN.md Feedback 章节作为持续反馈背景。
- Scenario：`gallery/sections/scenarios.tsx` 的 DetailPageStructureScenario 展示 Alert Stack 与 Hero，支持对象上下文与恢复动作分工；Buttons' Gap 已读，但尺寸不纳入规则。
- 外部：[APG Alert](https://www.w3.org/WAI/ARIA/apg/patterns/alert/) 支持重要消息不夺取任务焦点、区别 Alert Dialog；[Carbon Notification](https://carbondesignsystem.com/components/notification/usage/) 支持流内持续通知与短暂 Toast 的区分。静态中性指导不必采用紧急播报是根据实际角色可覆盖与通知语义作出的判断。

### sonner — Sonner

- 本地：`src/components/ui/Sonner/index.tsx`、`src/components/ui/useToast.ts`、`gallery/sections/overlays.tsx:203` SonnerDefaultContent、`gallery/gallery-demos.tsx:30` SonnerPreview。区分静态预览与真实通知；包装器公开 add / action 配置，不暴露上游全部 API。CONVENTIONS.md 规定单一通知宿主。
- ADM：`../axo-app-fe/app-design-mock/src/pages/config/index.tsx` 的保存结果与空字段提示；仅证明通知使用场景。空字段仅用 Toast 告知不是正式推荐，Reference 优先字段反馈。
- Scenario：FloatingSurfaceSamples 将反馈与提示 / 选择 / 模态区分；CopyButtonFeedbackScenario 证明已充分表达的就地复制反馈无需等义全局通知。
- 外部：[Carbon Notification](https://carbondesignsystem.com/components/notification/usage/) 支持时间性通知与持续信息边界。Sonner 站点和 GitHub 搜索得到的旧 toast.mdx 地址未成功读取，不把搜索摘要当作规则证据；封装行为直接核对本地源码，无阻塞。

### empty-state — Empty State

- 本地：`src/components/empty-state/index.tsx`、`gallery/sections/feedback.tsx:112`。区分 block 的说明 / 操作和 inline 的图标 / 标题；组件不拥有加载判定。
- ADM：`../axo-app-fe/app-design-mock/src/pages/me/design-credentials/index.tsx:58` 的凭证空集合、`components/resource-share-dialog/collaborators.tsx:113` 的局部空缺。DESIGN.md Empty State 区分空、加载与失败。
- Scenario：Resource Sharing 的协作者空态；Detail Page Structure 的独立内容区域关系。未把尺寸规则扩写到本文。
- 外部：[Carbon Loading](https://carbondesignsystem.com/patterns/loading-pattern/) 仅辅助核对加载占位与结果的时间边界，空态规则以本地契约和已知结果语义为主。

### progress — Progress

- 本地：`src/components/ui/Progress/index.tsx`、`gallery/sections/feedback.tsx:71`、`docs/temporary-component-cleanup.md:14`、`docs/components-content-migration.md:61`。确定值 / null、不再暴露独立标签轨道部件；没有任务执行或估时逻辑。
- ADM：搜索 `../axo-app-fe/app-design-mock/src/**/*.tsx` 未核验直接 Progress 调用，ProgressiveLoginScreen 名称匹配不计为使用证据。背景仅采用 DESIGN.md Loading 的已知进度原则。
- Scenario：当前 registry 无直接进度语义 Scenario。
- 外部：[Base UI Progress](https://base-ui.com/react/components/progress) 确认 null 表示不确定状态；[Carbon Loading](https://carbondesignsystem.com/patterns/loading-pattern/) 辅助区分加载指示与完成比例。未把上游演示随机计时增长当作真实业务进度规范。

### spinner — Spinner

- 本地：`src/components/ui/Spinner/index.tsx`、`gallery/sections/feedback.tsx:101`、`docs/component-contract-update.md`。只有加载图标与可选名称，没有成功 / 失败自动状态。
- ADM：`../axo-app-fe/app-design-mock/src/pages/session/jobs-panel/job-status-badge.tsx` 中运行状态分支；该图标受 Badge 内容类型影响，不能将调用即视为已正确展示。异步范围另由状态文字支撑。
- Scenario：当前 registry 无独立 Spinner 语义 Scenario。
- 外部：[Carbon Loading](https://carbondesignsystem.com/patterns/loading-pattern/) 支持局部加载只表示进行中、不表示比例。未采用全屏加载或固定时间阈值作为强制规则。

### skeleton — Skeleton

- 本地：`src/components/ui/Skeleton/index.tsx`、`gallery/sections/feedback.tsx:89`、`docs/component-contract-update.md`。只提供占位外形，生命周期由调用方决定。
- ADM：`../axo-app-fe/app-design-mock/src/pages/design/files/components/file-table/index.tsx:38` 的骨架行与保留表头，核对了实际结构。
- Scenario：无直接骨架语义 Scenario。
- 外部：[Carbon Loading](https://carbondesignsystem.com/patterns/loading-pattern/) 仅支持已知数据内容的结构占位与局部加载区分；避免虚假可操作控件是结合该语义和当前实现作出的判断。

### scrollbar — Scrollbar

- 本地：`src/components/ui/Scrollbar/index.tsx`、`gallery/sections/feedback.tsx:19`、`docs/table-scroll-area.md`。确认绑定所属 Base UI ScrollArea、Thumb 内化、没有外部受控数字接口。文档旧 TableBody / TableRow 示例已被当前 native tbody / tr 取代，不沿用旧导出。
- ADM：`../axo-app-fe/app-design-mock/src/components/resource-share-dialog/bulk-invite-dialog.tsx`，单一 viewport 与候选树。
- Scenario：FileFolderPickerScenario、Resource Sharing 的 BulkInviteDialog 及 Detail Page Structure 中的独立内容范围，支持模态边界与内容滚动各自职责。
- 外部：[Base UI Scroll Area](https://base-ui.com/react/components/scroll-area) 支持 Root / Viewport / Content / Scrollbar 与真实原生滚动关系；没有推导任意滑块或数据分页能力。

### bar-chart — Bar Chart

- 本地：`src/components/ui/BarChart/index.tsx` 与 `NOTICE.md`、`gallery/sections/temporary.tsx:188`、`docs/component-contract-update.md`。registry 明确将其提升到 Foundations。确认单组非负柱高、共同比例、标签 / Tooltip 和可选图例；没有专门选择 / 钻取契约。
- ADM：搜索 `../axo-app-fe/app-design-mock/src/**/*.tsx` 未核验到 BarChart 直接使用。不存在可引用的产品示例，不制造场景落点。
- Scenario：当前 registry 无图表语义 Scenario。
- 外部：[Carbon Chart types](https://carbondesignsystem.com/data-visualization/chart-types/)、[Carbon Simple charts](https://carbondesignsystem.com/data-visualization/simple-charts/) 支持比较与组成的选型区分。负值限制直接来自本地 Math.max(0, value)，不推广为柱形图普遍限制。

### pie-chart — Pie Chart

- 本地：`src/components/ui/PieChart/index.tsx` 与 `NOTICE.md`、`gallery/sections/temporary.tsx:202`、`docs/component-contract-update.md`。确认过滤非正值后求和、默认 Tooltip 显示原值、空总体仅显示占位图形；不将空图解释成业务空态。
- ADM：搜索 `../axo-app-fe/app-design-mock/src/**/*.tsx` 未核验到 PieChart 直接使用；正式例子为通用桌面场景。
- Scenario：当前 registry 无直接饼图语义 Scenario。
- 外部：[Carbon Chart types](https://carbondesignsystem.com/data-visualization/chart-types/) 与 [Carbon Pie Charts](https://charts.carbondesignsystem.com/pie) 支持部分 / 整体语义。互斥同口径分类、共同总体与原值格式化判断结合本地求和实现推导。

### topbar — Topbar

- 本地：`src/components/ui/Topbar/index.tsx`、`gallery/topbar-demo.tsx`、`gallery/sections/navigation.tsx:51`、`docs/topbar.md`。确认内容类型、每个尾部按钮的独立菜单、调用方关闭和导航职责。文档明确 Gallery 惰性按钮不是产品事件。
- ADM：`../axo-app-fe/app-design-mock/src/components/toolbar/PageToolbar.tsx` 的 portal、路由 Breadcrumb 与应用侧栏控制。旧 DESIGN.md Toolbar 名称只作背景，不误写回已删除组件。
- Scenario：Buttons' Gap 的操作组范围、Floating Surfaces 中 Dialog 的任务边界；Detail Page Structure 中 Hero / Section 的内容职责。具体间距与视觉补偿未纳入规则。
- 外部：Topbar 是本地组合契约，未因为上游存在 Toolbar primitive 就推断具有完整 toolbar 键盘或导航模式。

## 已解决的研究差异

Avatar 缺少 src 的 fallback 不等同于图片请求失败 fallback；Badge 的 icon 必须配合内容类型；Content Group 的 count 与 hidden 具有不同可访问内容范围；Sonner 上游文档抓取失败改为本地公开包装器加官方通知语义交叉验证。上述问题已有有依据的判断，无需产品确认。历史文档的组件子部件、旧名称与旧缺省值均未覆盖当前实现。

## 消息、输入与问答：研究记录

本节是研究阶段的临时记录，可以删除，不属于 Skill 运行时规则。范围由当前 Gallery registry 的 general + composite 及 inventory.json 核对。已读取本仓库 AGENTS.md、HANDOFF.md、组件 CONVENTIONS，以及 ADM 根目录 AGENTS.md、AGENTS.design.md；Git user 为 XuWeinan123，ADM 全程只读。ADM 路径均相对于 `../axo-app-fe/`。ADM DESIGN.md 的 Components、Message、Lightbox、Tooltip、Feedback 和 Badge 仅作背景，不独自决定正式规则。当前公开实现和最新 HANDOFF 优先于历史文档与 Gallery 陈旧描述。

### composer — Composer

- 本地：`src/components/ui/Composer/index.tsx`、`ComposerBase.tsx`；`gallery/sections/messages.tsx` 的 ComposerDemo 和 composer 注册；`gallery/composer-attachment-preview-demo.tsx`；`docs/composer-single-line.md`、`docs/composer-spacing.md`。确认自由请求输入、调用方草稿/提交/上传/权限归属，以及完整布局的上下文与附件槽。
- ADM：`app-design-mock/src/pages/session/composer/index.tsx:222` 起、`responsive-composer.tsx`。实际会话输入将文字、附件、项目与授权状态映射给库组件；证明多材料请求真实存在，不继承其中的业务提交规则。
- Scenario：已读 `gallery/scenarios/buttons.tsx` Buttons' Gap 和 `gallery/sections/scenarios.tsx` 注册，采用同一请求内的主路径与操作分组语义，不把尺寸与间距值写进 Reference。
- 外部：[Carbon Chatbots usage](https://carbondesignsystem.com/community/patterns/chatbot/usage/) 支持用户意图输入与提交、附加输入按钮组成一个请求入口；没有照搬其视觉或业务约定。

### composer-inline — Composer Inline

- 本地：`src/components/ui/ComposerInline/index.tsx`、`Composer/ComposerBase.tsx`；`gallery/sections/messages.tsx:203`；`gallery/composer-single-line-demo.tsx`；`docs/composer-single-line.md` 和 `docs/composer-spacing.md`。确认紧凑入口使用 textarea，可换行；不接受附件槽或 Context Bar，使用 contextDropdown；上传和执行仍由调用方负责。
- ADM：`app-design-mock/src/pages/session/composer/responsive-composer.tsx:24` 起，将附件放在 header 相邻结构、上下文映射到 contextDropdown。实际做法支持完整/紧凑入口共享同一请求，但不将其断点作为通用规则。
- Scenario：Buttons' Gap，已读 `gallery/scenarios/buttons.tsx`；只采用关联动作的层级判断。
- 外部：[Carbon Chatbots usage](https://carbondesignsystem.com/community/patterns/chatbot/usage/) 支持输入与提交的统一请求语义。文档中早期“两个入口都接受 Context Bar”的描述已被文末修订和当前类型明确覆盖，不构成未决事项。

### composer-context-bar — Composer Context Bar

- 本地：`src/components/ui/ComposerContextBar/index.tsx` 与 ComposerBase；`gallery/sections/messages.tsx:215`；`docs/composer-single-line.md` 文末修订。确认仅一个前置 Dropdown，没有 trailing/children 插槽；它选择请求上下文，不承担历史导航或任意工具栏职责。
- ADM：`app-design-mock/src/pages/session/composer/context-bar/index.tsx`，项目选择传入 contextBar.dropdown，恢复待回答入口置于 header；`responsive-composer.tsx` 映射紧凑入口。仅作为同一请求上下文和独立恢复操作的真实例证。
- Scenario：Buttons' Gap 与 Floating Surfaces 中 DropdownSurfacePreview 已读；后者区分单值选项与动作浮层，具体浮层样式不在本 Skill 范围。
- 外部：未额外采用外部规则；公开类型与当前组合已足以明确本项目专用结构。

### composer-attachment — Composer Attachment

- 本地：`src/components/ui/ComposerAttachments/AttachmentCard.tsx`、`types.ts`、`index.tsx`；`gallery/sections/messages.tsx:238`、ComposerAttachmentPreviewDemo；`docs/composer-attachment-preview.md`。核对单卡 state 由外层显式传入、上传和预览失败不同、卡片与集合预览职责不同、集合只导航 uploaded 文件。
- ADM：`app-design-mock/src/pages/session/composer/attachment/index.tsx`，消费者将 UI 身份映射回上传文件对象，使用 ComposerAttachments、外部预览描述与移除回调。仅支持草稿材料管理场景，不把上传 service 归入库能力。
- Scenario：当前注册没有针对上传卡片的专门语义 Scenario；Lightbox 相关 Buttons' Gap 已检查，不添加尺寸规则。
- 外部：[WAI-ARIA APG Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) 只支持进入完整预览后的模态边界；上传/预览状态区分以本地契约为准。

### message-query — Message Query

- 本地：`src/components/ui/MessageQuery/index.tsx`、`Message/types.ts`、`Message/shared.tsx`、`Message/MessageFooterSlot.tsx`；`gallery/sections/messages.tsx:254`、MessageAttachmentDemo、`gallery/message-custom-footer-demo.tsx`；`docs/message-split.md`、`docs/message-custom-footer.md`，并读 Message sizing/ordered-blocks 的历史提示。确认用户输入、消息身份和通用 footer 插槽，不引入组件内队列状态。
- ADM：`app-design-mock/src/components/chat-message/index.tsx`、`pages/session/followups/message.tsx`。实际分别映射用户消息材料和独立排队消息；队列/编辑资格由产品拥有，不将占位回调当成完整推荐实现。
- Scenario：Actions' Gap `gallery/scenarios/actions.tsx` 和复制按钮反馈 `gallery/scenarios/resource-sharing.tsx:286` 已读，适用于附属 Footer。正式 Reference 只采用操作归属与复制反馈的真实结果。
- 外部：[Carbon Chatbots usage](https://carbondesignsystem.com/community/patterns/chatbot/usage/) 支持 User Message 与系统回复的来源区别。陈旧 Gallery 说明只提 hover，当前实现还允许常显和替代 Footer，已按新契约处理。

### message-answer — Message Answer

- 本地：`src/components/ui/MessageAnswer/index.tsx`、`Message/types.ts`、`Message/shared.tsx`、`Message/ArtifactList.tsx` 的关联入口；`gallery/sections/messages.tsx:264` 及 MessageAttachmentDemo；`docs/message-activity.md`、`docs/message-split.md`、`docs/message-ordered-blocks.md`、`docs/message-custom-footer.md`。当前块为 markdown/activity/custom；默认复制仅包含 Markdown，自定义复制由调用方明确提供。
- ADM：`app-design-mock/src/components/chat-message/answer.tsx`，按原序转换工具/思考/提问块，保持一个 MessageAnswer 和一组页脚，并明确生成 copyText。此处证明复杂回答场景，不固化其业务 block 名。
- Scenario：Actions' Gap、复制按钮反馈已读，限页脚及复制反馈；无专门要求 Answer 改变块顺序的 Scenario。
- 外部：[Carbon Chatbots usage](https://carbondesignsystem.com/community/patterns/chatbot/usage/) 支持系统回复与结构化回应、卡片之间的职责区别。旧 docs 的 status/tool-calls 示例明确标为历史，采用当前 activity 契约，不留未决。

### message-footer — Message Footer

- 本地：`src/components/ui/MessageFooter/index.tsx`、`Message/MessageFooterSlot.tsx`、`Message/shared.tsx`；`gallery/sections/messages.tsx:273`；`gallery/message-custom-footer-demo.tsx`；`docs/message-custom-footer.md` 和 HANDOFF 最新 caller-owned message footers。核对 timeActions/text、actions 数组替换/函数扩展、onEdit 才出现 Edit、无 align/showCancel/业务队列能力。
- ADM：`app-design-mock/src/pages/session/followups/message-footer.tsx`、`message.tsx`。实际页脚以 text 显示消息状态，再以 activeFooter 提供独立消息操作。示例中的发送/编辑占位行为不当作真实服务能力。
- Scenario：`gallery/scenarios/actions.tsx`、`gallery/scenarios/resource-sharing.tsx:286`，分别核对动作组以及复制成功后反馈。Reference 不规定样式数值。
- 外部：未额外引入外部行为；本地最新契约足以明确页脚语义。Gallery 的队列 demo 用 disabled text action 表示状态，而 API 有纯 text 类型；正式规则采用纯状态用 text 的最佳判断，不复制该展示方法。

### message-activity — Message Activity

- 本地：`src/components/ui/MessageActivity/index.tsx`；`gallery/sections/messages.tsx:293` 及 MessageActivityPreview；`docs/message-activity.md`；MessageAnswer 的 activity 分支。确认具名过程摘要、可选披露、running/stay/failed；stay 不自动声明成功，空白详情不创建触发器。
- ADM：`app-design-mock/src/components/chat-message/answer.tsx:48` 起，将工具和思考记录转换为 activity props；失败状态也映射为独立 activity。属于经核验的间接使用，并非未找到调用。
- Scenario：当前 registry 无 Message Activity 专门 Scenario；复制按钮场景只作用于其外部消息页脚，不将展开详情与复制混为一体。
- 外部：[WAI-ARIA APG Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) 支持摘要触发器控制对应内容显隐；这不等于任务执行、批准或重试。外部规则与当前本地行为一致。

### message-job-card — Message Job Card

- 本地：`src/components/ui/MessageJobCard/index.tsx` 公共 props/status 和渲染；`gallery/sections/messages.tsx:322`，以及 MessageAttachmentDemo 中 Answer card 组合。没有发现专门组件文档；Message split 的 card 示例只用于确认组合位置，旧 props 不沿用。
- ADM：`app-design-mock/src/components/design-mock/session-message-content/index.tsx:95` 起，建议接受后创建演示 Job、回填 accepted，并提供查看入口。该路径是演示逻辑，只证明建议—决策—结果场景存在，不宣称当前生产创建能力。
- Scenario：Buttons' Gap，已读 `gallery/scenarios/buttons.tsx`；采用同一建议中的接受与拒绝属于一个决策组，不抄录样式数值。
- 外部：[Carbon Chatbots usage](https://carbondesignsystem.com/community/patterns/chatbot/usage/) 支持卡片为显著动作提供补充信息。任务建议/创建状态的细节以本地接口为准。

### message-media — Message Media

- 本地：`src/components/ui/MessageMedia/index.tsx`、`Lightbox/index.tsx`、`LightboxContent.tsx`；`gallery/sections/messages.tsx:334` 与 MessageAttachmentDemo；`docs/lightbox.md`、`docs/message-split.md`。确认仅图片/视频、内部 Lightbox、视频预览与完整播放不同、失败时禁用入口。
- ADM：`app-design-mock/src/components/chat-message/query-media-attachments/index.tsx`、`pages/session/message/media-artifacts/index.tsx`。前者映射用户附件，后者映射回答产物。仅证明资源身份、预览与下载映射真实存在，不继承按媒体数量自动选样式的业务阈值。
- Scenario：当前 registry 无媒体预览专属语义 Scenario；Lightbox 的按钮组合适用 Buttons' Gap，已读。
- 外部：[WAI-ARIA APG Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) 支持点击媒体进入完整模态预览的边界；未把悬停播放视为独立任务执行。

### session-end — Session End

- 本地：`src/components/ui/SessionEnd/index.tsx`；`gallery/sections/messages.tsx:226` 和 SessionEndPreview。确认替代不可用 Composer 的会话边界、解释与可选行内操作；未发现独立组件 docs。
- ADM：`app-design-mock/src/pages/session/index.tsx:460` 起，只读会话显示 SessionEnd 与创建副本入口，非只读分支显示 Composer。副本入口为演示动作，不宣称已经具备复制服务。
- Scenario：无专门适用 Scenario；行内操作语义按 CONVENTIONS 的 a 导航/button 操作约定，未扩展一般链接样式检查。
- 外部：没有借用额外外部规则；当前组件说明、实现与只读场景已足以解释“不能继续输入”不等于“任务成功完成”。

### session-info — Session Info

- 本地：`src/components/ui/SessionInfo/index.tsx`；`gallery/sections/navigation.tsx:203` 和内联渲染。确认纯展示 section、可选来源行、人物/时间行和 Badge，不拥有浮层触发或导航；未找到独立专门 docs。
- ADM：`app-design-mock/src/views/side-bars/main/history/session/session-info/index.tsx`，调用方 PreviewCard.Popup 包含 SessionInfo，展示来源、创建者、创建时间和只读 Badge；侧栏条目的导航另有归属。
- Scenario：`gallery/sections/scenarios.tsx` SidebarStatementsScenario 已读，侧栏条目内短元信息与动作切换不同于整张会话详情卡；FloatingSurfacesSamples 也已读，但不将 Tooltip 复制成会话卡。
- 外部：未额外引入外部规则，展示职责与各字段含义由本地明确定义；ADM DESIGN.md Tooltip 背景用于排除只在悬浮层放关键操作的误用。

### turn-navigator — Turn Navigator

- 本地：`src/components/ui/TurnNavigator/index.tsx`、公共导出 `src/components/ui/index.ts:278`；`gallery/sections/messages.tsx:309` 与 TurnNavigatorDemo。确认 items/activeId/onSelect 纯呈现契约，组件只对空集合不渲染，不自动检测够长会话或滚动。
- ADM：`app-design-mock/src/pages/session/index.tsx:400` 起，hasTurnNav 控制挂载、activeTurnId 跟随会话、scrollToTurn 执行定位。支持当前会话内导航，与 Pagination 的数据分页不同。
- Scenario：当前 registry 未提供轮次导航的专门 Scenario；没有将 Sidebar Statements 的条目状态规则错误用于轮次选择。
- 外部：未引入额外外部规则；本地导航地标、目标列表、回调与实际滚动场景已明确边界。Gallery“足够轮次/空间才出现”归调用方，未虚构为组件自动能力。

### ask-user — Ask User

- 本地：`src/components/ui/AskUser/index.tsx`、`AskUserInputOption.tsx`；`gallery/sections/composites.tsx:510` 与 AskUserDemo/ASK_USER_ITEMS；公共类型 TAskUserItemDefinition、TAskUserItemType、TAskUserActions。未发现独立问答 docs。确认逐题结构、未回答前進按 Skip、最后题提交，以及单选预设选项自动前进。
- ADM：`app-design-mock/src/pages/session/composer/ask-user/index.tsx`、`components/chat-message/question-card/index.tsx`。已读前者完整流程与后者实际 Root/Item/Options 调用，支持问答用于任务澄清、业务回包由消费者负责；不将其提交约定强加给库。
- Scenario：Buttons' Gap，已读 `gallery/scenarios/buttons.tsx`，适用于返回/继续/提交的同一任务层级。无单独问答 Scenario。
- 外部：[Carbon Chatbots usage](https://carbondesignsystem.com/community/patterns/chatbot/usage/) 支持结构化回答用于补充任务信息；[WAI-ARIA APG Radio](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) 支持单选组一次至多一个答案。当前自动前进是本项目问答行为，不能反推普通 Radio 都应自动前进。已明确不把选择、跳过或关闭等同于业务授权，无核心待定问题。

### ask-user-option — Ask User Option

- 本地：`src/components/ui/AskUser/index.tsx` 的 Item/Options/Option 与公开类型，`AskUserInputOption.tsx`；`gallery/sections/composites.tsx:527` 与 AskUserOptionDemo。确认答案依赖 Root/Item，single 预设项前进、multiply 保留多选，Options 固定追加自定义输入；独立 Option isInput 用于明确组合，不在常规 Options 中重复添加。
- ADM：`app-design-mock/src/pages/session/composer/ask-user/index.tsx:76` 起和 `components/chat-message/question-card/index.tsx:42` 起，分别按题目选择模式生成 Option，先滤除后台 Other，再让 Options 添加自定义输入。该组合证明避免重复 Other 的真实必要性。
- Scenario：同父组件 Ask User，Buttons' Gap 仅用于题目外部动作组；没有额外选项样式规则。
- 外部：[WAI-ARIA APG Radio](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) 支持互斥选择组；[Carbon Chatbots usage](https://carbondesignsystem.com/community/patterns/chatbot/usage/) 支持结构化答案与操作卡片的区别。未宣称 Option 具有普通独立按钮的任意行为。

### ask-user-option-symbol — Ask User Option Symbol

- 本地：`src/components/ui/AskUserOptionSymbol/index.tsx`、`AskUser/index.tsx` 中的 ChoiceShortcut、`AskUser/AskUserInputOption.tsx`；`gallery/sections/composites.tsx:545`。确认默认 aria-hidden span、interactive 才是按压按钮；自定义已填写答案用该入口重新选择，selected 反映答案，不代表正确或成功。
- ADM：没有核验到直接独立使用 AskUserOptionSymbol 的调用。已核验 `app-design-mock/src/pages/session/composer/ask-user/index.tsx` 中 Options 的真实使用，Symbol 由库内部提供，属于明确的间接场景而非杜撰独立调用。
- Scenario：没有适用的独立 Symbol 场景；父组件的按钮组规则不扩张成 Symbol 必须可点击的要求。
- 外部：[WAI-ARIA APG Radio](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) 仅用于答案选择状态的背景；独立标识何时成为重新选择入口以当前实现为准。

### 已调查并解决的历史冲突

- Message split/ordered-blocks/sizing 保留旧 Message、status、tool-calls 示例；已采用当前 MessageQuery/Answer、activity/custom 契约，历史页脚参数不进入正式规则。
- HANDOFF 早期 Footer 的 showCancel、timeActionsText/action 三种形态已经被最新两形态和通用 actions 覆盖；最新实现为唯一能力基线。
- Composer 单行文档含累积修订，当前 Inline 类型排除 Context Bar 和 attachments，使用 contextDropdown；没有按旧段落虚构能力。
- Message Custom Footer Gallery 演示将排队状态画为 disabled action；新 Reference 依据现有 text 类型与状态语义推荐纯文本，而非复制演示表现。
- Guide Card、Lightbox、Code Block 的后续证据由 data_structure 代理负责；本片段只覆盖以上 16 个正式 ID。

上述冲突均可由当前实现、类型和明确修订解决，没有必须由用户确认的核心语义问题。

## 补全三项内容组件的研究证据

研究阶段临时记录，可删除；正式 References 不依赖此文件。已遵守先读 ADM `AGENTS.md` / `AGENTS.design.md` 的要求，ADM 全程只读。以下依据以当前公开实现和类型为准；产品历史调用仅证明相应场景存在。

### lightbox

- 本地：`src/components/ui/Lightbox/index.tsx` 的 LightboxProps、TLightboxType、TLightboxState 与完整外壳；`LightboxContent.tsx` 的显式渲染选择及 loading / failed 优先级；`LightboxDocument.tsx` 的文档内容、独立读取状态与重试；`src/components/ui/index.ts:156` 的公开导出。已读 `docs/lightbox.md`，并核对 `docs/composer-attachment-preview.md` 的预览与上传职责。当前类型包括 image / video / text / codeblock / html / document / custom / unsupported；Reference 不靠类型枚举代替语义。
- Gallery：`gallery/sections/overlays.tsx:305` 的正式 Panel、LightboxDemo、LightboxInteraction 与共享 LightboxContent，已读预览内容和完整浮层两类示例。确认内嵌示例不是另外一种非模态产品 API。
- ADM：已读 `../axo-app-fe/app-design-mock/src/pages/design/files/detail/index.tsx:534` 的当前文件身份、内容类型、预览开合和下载目标；已读 `src/pages/session/message/lightbox-demo/index.tsx:34` 的文件集合切换、边界与状态。后者为明确演示场景，其定时模拟不证明真实请求行为；前者的 custom PDF 与加载包裹也不覆盖库当前已有的 document / state 能力。
- Scenario：没有 Lightbox 专属任务语义 Scenario；已检查注册，读取 `gallery/scenarios/buttons.tsx` 的 Buttons' Gap，只有按钮分组与不同导航目标的职责适用，Reference 不写尺寸。Code Block 作为内嵌内容时，其复制动作可参考 `gallery/scenarios/resource-sharing.tsx:286` 的 CopyButtonFeedbackScenario。
- 官方：[Base UI Dialog](https://base-ui.com/react/components/dialog) 支持当前外壳的模态上下文；[MDN code](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/code) 支持代码内容与预览外壳的分工。没有将 Base UI 未经当前 LightboxProps 暴露的能力写成本地 API。
- 采用判断：文件身份、预览内容、相邻范围与下载对象必须一致；读取失败不等于上传失败或不支持格式。Lightbox 是聚焦预览，复杂编辑管理任务应评估 Sheet Basic，而非因 custom 槽存在就扩大预览职责。

### code-block

- 本地：`src/components/ui/CodeBlock/index.tsx` 的 CodeBlockProps 与完整组件；`highlight.ts` 的语言解析与原文回退；`src/components/ui/index.ts:60` 的公开导出。已读 `docs/release-0.19.0.md` 的公开组件说明。确认展示模式、复制结果和原始 code 的关系，没有编辑、执行或校验代码功能。
- Gallery：`gallery/sections/composites.tsx:489` 的正式 Panel 与 `gallery/code-block-demo.tsx`，已读高亮模式、复制文案、显示方式与当前内容输入。示例中的 TypeScript 不是限制可用语言的语义规则。
- ADM：已读 `../axo-app-fe/app-design-mock/src/components/markdown-render/code-block.tsx`，确认 Markdown 中代码片段经 CodeBlock 阅读 / 复制；已读 `src/pages/design/projects/detail/prompt-section.tsx:59`，确认现有产品也用它读取需要原样复制的 Prompt，并由独立 Dialog / InputArea 编辑。这个实例仅支持有原文读取需求的条件性使用，不支持把所有普通说明统一代码化。
- Scenario：没有独立 Code Block 语义 Scenario；Buttons' Gap 与 `gallery/scenarios/resource-sharing.tsx:286` 的 CopyButtonFeedbackScenario 已读，仅提炼操作分工与真实复制成功反馈，不复制视觉数值。
- 官方：[MDN code](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/code) 支持代码表示及多行内容结构。高亮、复制和非代码原文使用边界由本地实现及明确的读取任务共同决定。
- 采用判断：阅读 / 复制与编辑 / 执行分开；高亮失败时内容仍可作为原文阅读，不能推定原文错误；复制成功须依据真实结果，而不是点击事件。

### recommendation-panel

- 当前正式名称为 Guide Card，Gallery ID 保留 `recommendation-panel`。本地：`src/components/ui/GuideCard/index.tsx` 的 GuideCardProps、GuideCardItem 与完整实现；`src/components/ui/index.ts:343` 的公开导出；`docs/guide-card.md`。确认未完成行调用 onItemClick(id)，已完成行只读，完成值来自 items[].checked，没有 footer、buttonProps 或自动下一步计算。
- Gallery：`gallery/sections/composites.tsx:484` 的正式 Panel 与 `gallery/recommendation-demo.tsx` 已读。Panel 描述仍提及 action button，当前 Demo 和文档已经是行入口模型；正式 Reference 按当前实现编写。Demo 中固定完成项、空回调和展示任务文案不作为业务规则。
- ADM：已读 `../axo-app-fe/app-design-mock/src/views/side-bars/main/user-profile/index.tsx:63` 的 GuideCard；调用方控制 guideOpen、关闭及状态数据。onItemClick 当前绑定演示提示，只证明调用边界，不证明已实现真实导航或实际完成结果。
- Scenario：没有专属 Guide Card Scenario。已检查当前注册，并阅读 Buttons' Gap 作为内部 Topbar 及其他任务入口的组合背景；不将尺寸规则纳入 Reference。
- 官方：[GOV.UK Task list](https://design-system.service.gov.uk/components/task-list/) 支持事项身份、完成状态与进入任务的区别，以及任务清单不等于强制顺序流程。该官方组件可以链接已完成事项，而当前 GuideCard 完成行只读；Reference 明确保留本地能力边界，不将外部能力移植为承诺。
- 采用判断：完成标记是事实反馈，不是用户选择；点击入口不等于完成任务。多个事项的状态不同于 Progress 的单任务程度，也不同于 Message Job Card 的单项建议处理。

三项的来源差异已经由当前公开实现和文档解决，没有需产品确认的核心语义未决事项。未修改 ADM、组件实现或 Gallery。
