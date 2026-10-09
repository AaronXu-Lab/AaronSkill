# canvas-kit

aw-canvas-design 的画布标准件，包含流程模式和设计平铺模式。HTML 最初从流程画布抽出；卡片、视口控件和隔离预览两模式共用，入口旗、出口、判断、连线、流程树目录只适用于流程模式。新画布复制适用部分，再填所选模式数据：**视觉以适用的 HTML 标准件为准，逻辑以对应模式的 `reference/` 参考实现为准。**

## 目录

| 文件 | 内容 |
| --- | --- |
| `kit.css` | 全部 `--ck-*` token 与组件样式，HTML 标准件和参考实现共用 |
| `kit.js` | 仅供 HTML 标准件演示：内联图标（Phosphor Icons，MIT）与最小交互；参考实现不依赖它 |
| `index.html` | 标准件目录 |
| `page-card.html` | 页面卡片（方向 C：顶栏 / 预览 / 底栏）、入口小旗、出口、场景切换、加载骨架、选中态、宽页面 |
| `decision-node.html` | 判断节点（判断依据直接显示） |
| `reference-node.html` | 引用节点（单行，跨流程箭头） |
| `note-node.html` | 说明节点（单行，正文折叠） |
| `edge-styles.html` | 主路径 / 分支 / 异常三种线、扇出主干、同条件汇入、标签、呈现状态、悬停出口的临时去向线 |
| `sidebar.html` | 目录面板（侧栏组合、文件夹分组、连线筛选）与收起后的展开按钮 |
| `legend.html` | 一行图例（节点 + 连线两组，可收起） |
| `controls.html` | 右下角视口控件组及置灰态 |
| `canvas-shell.html` | 整页组合：中性淡灰画布、点阵、浮动目录、卡片与连线、图例、控件 |
| `reference/` | React + @xyflow/react + elkjs 参考实现（见下文） |

所有 HTML 都可以直接用浏览器打开（包括 `file://`），不需要构建。组件尺寸是画布缩放 100% 时的像素；`canvas-shell.html` 按 0.6 缩放展示整体效果。

## 在项目里使用

0. **核实现有能力**：先检查项目已有画布、框架和依赖；能满足本次需求就沿用，不为对齐参考版本而升级。确需新依赖时按项目约定选择兼容版本并取得所需授权。
1. **复制**：把 `canvas-kit/` 复制到项目的画布目录，画布路由挂在所属业务路由下（`/<业务路由>/design-canvas`）。
2. **映射 token**：项目有设计系统时，把 `kit.css` 顶部的 `--ck-*` 映射到项目 token（例如 `--ck-ink: var(--color-on-surface)`），组件结构与尺寸不变；缺少的中性灰等 token 在设计系统中补齐。
3. **换成设计系统组件**：有 Sidebar、Dialog、Tooltip、Button 时，用它们搭出与标准件同等的效果，不自写树、弹窗和提示。侧栏组合按项目实际导出核实；平铺使用组件类型 Section Group → 业务模块 Item，无文件夹/折叠树。没有同名 `SidebarSectionGroup` 时复用已有 Section/Header/Item 组合，不能虚构 API。
4. **填模式数据**：流程参照 `reference/flows.example.ts`；平铺参照 `reference/tiles.example.ts`，类型组下直接模块，模块内每个流程/相关场景组一行；接好真实组件、独立入口与尺寸/重置桥接。平铺实现细则见下节。
5. **逐项对照**：打开对应 HTML 标准件与自己的画布并排比较，再按 SKILL 的验收矩阵检查。

## 设计平铺接入

读取 [平铺建模与比较](../../references/design-tiling.md)。`types.ts`、`layout.ts`、`board.tsx`、`sidebar.tsx` 与流程路由例子仍是流程专用实现，不能传空 `edges` 当作平铺。平铺改用 `tiles.ts` 的独立集合/类型/模块/行/条目模型及 `layoutTiles`，目录参照 `tiles-sidebar.tsx`；组下仅直接模块 Item，卡片实例由模块内的行、清单/搜索及独立查看入口逐项呈现。

宿主渲染器接入规则：

- 选择模块后，将该模块的行与全部条目传给平铺计算器（保留对应类型组与模块元数据），用稳定 ID 接入现有画布库节点；每个有依据的流程/相关场景组一行，不自动换行，独立场景单卡成行。多模块概览可传完整集合。节点位置取 `positions`，行标题取 `rowTitles`；渲染 `sequence` 状态与证据，`unverified` 明显标记“顺序待核实”。
- 输入实测外部卡片尺寸；同组统一预览比例，尺寸变化重新计算平铺槽位、保留用户视口与手动偏移。`rowHeaderHeight` 为行标题/状态预留空间，不与卡片重叠。宽流程允许横向平移，重置布局清偏移但不清场景状态。
- 复用实际展示组件、卡片三段结构、说明、重置、拖拽命中区、视口控制及 `preview-frame.tsx` 的隔离承载能力；使用独立平铺卡片适配器，不渲染 `node.tsx` 的流程 handles、入口旗、出口及判断，不启用流程连线筛选或 `checkLayout`。不能复制原业务 UI 作为适配器。
- `source-only` 显示记录/缺口和独立查看入口；`interactive` 才挂载原组件预览及重置。清单/搜索定位全部条目，按需加载只减少同时挂载数，不减少覆盖；`tileCoverage` 分别计数，不把引用可达当交互验证。
- 所有 UI 标签通过项目国际化机制（示例为 `titleKey` / `t`）。选中模块的路由可用 `?mode=tiles&module={id}`，单条目用 `?item={id}`；源码记录与真实预览各有明确结果。

`tiles.ts` 是框架中立的布局/模型参考，`tiles-sidebar.tsx` 是侧栏组合示例；宿主原组件适配器、平铺画板/卡片渲染及路由需按项目实现，不宣称这些文件是完整可运行应用。

## 尺寸桥接适用范围

`preview-protocol.ts` 原样上报根元素矩形，`preview-frame.tsx` 收到后直接调整 iframe，适用于根尺寸不依赖 iframe 视口的测量壳。响应式 Dialog/Sheet 不应原样套用：先按原组件声明宽度和响应式留白给出安全视口，再按 [稳定尺寸规则](../../references/component-design.md#预览视口与稳定尺寸) 适配回算并有界检查收敛；否则 `vw/vh` 或百分比宽度可能持续缩小。首次尺寸上报撤骨架不是稳定性验收。两模式都需检查动态内容与底部操作。

## 参考实现（`reference/`）

此参考实现曾用 `react` / `react-dom` 19.3.0、`@xyflow/react` 12.11.6、`elkjs` 0.12.0 验证；这些版本不是目标项目的限制。`@phosphor-icons/react`（曾用 2.1.10）只是图标，可以换成项目图标。样式全部来自 `kit.css` 的类名。既有流程参考实现曾用 TypeScript strict 模式通过类型检查，并实际打包运行验证：连线指标通过、拖动几何自检通过，info Dialog 显示在画布之上，悬停出口时出现临时去向线。

| 文件 | 职责 |
| --- | --- |
| `tiles.ts` / `tiles.example.ts` | 平铺独立模型与示例：类型组、业务模块、显式行和来源/能力；实测行列布局、完整条目排序及分离覆盖计数，不依赖 ELK |
| `tiles-sidebar.tsx` | 平铺类型 Section Group → 直接业务模块 Item；无文件夹/折叠树，使用国际化键 |
| `types.ts` | 数据模型：节点四类（页面、判断、引用、说明）、边三类（主路径、分支、异常）、`exits`、`variants`、`parent` 两级；数据工厂函数 |
| `layout.ts` | ELK 选项与端口：24px 基线端口、右侧下半部分支端口、按条件分组的入口、单行节点底边入口、标签放末段 |
| `metrics.ts` | 连线指标自检，结果写到画板根节点的 `data-checks` |
| `reroute.ts` | 拖动后只平移首末段的 `rerouteOf`，以及拖动几何自检 `checkDragGeometry` |
| `edge.tsx` | 圆角正交路径与统一样式的标签 |
| `node.tsx` | 四类节点、入口小旗、info Dialog、重置场景、场景切换、出口（悬停去向线或提示）、nodrag 拖动命中区 |
| `preview-frame.tsx` | 隔离的 iframe 预览：限流加载、骨架、尺寸上报后撤骨架、0.5 缩放 |
| `preview-protocol.ts` | 画布与预览的 postMessage 协议：`size`（预览 → 画布）与 `reset`（画布 → 预览） |
| `sidebar.tsx` / `legend.tsx` | 目录与图例（通用 HTML 版；有设计系统时换成其组件） |
| `board.tsx` | 画板：默认视口适配全图、Shift+1 / Shift+2、右下控件、筛选与聚焦、悬停出口的临时线、拖动 reroute、`data-checks` |
| `flows.example.ts` / `canvas-page.example.tsx` | 示例流程与画布页路由（`?flow=`、`?preview=`、`?screen=`） |

不要用父级 `visibility: hidden` 保留已访问流程的画板：画布库会在节点上写行内 `visibility`，其他流程的卡片会透出来。想加快加载，优先给预览做轻量的独立入口页，避免每个 iframe 都启动整个应用。

## 平铺参考验证

布局行为检查（运行时支持 TypeScript 类型擦除的 Node；其他环境用已有 TS 测试运行器）：

```bash
node --experimental-strip-types --test aw-canvas-design/tests/tiles.test.mjs
```

测试覆盖逐行排列、宽卡片不压缩、动态尺寸后的不重叠、源码记录保留、完整条目覆盖、计数区分及无效关系拒绝。模式选择与边界自查见 [走查用例](../../tests/mode-routing.md)；这些检查不替代宿主浏览器中的组件交互和尺寸收敛验收。
