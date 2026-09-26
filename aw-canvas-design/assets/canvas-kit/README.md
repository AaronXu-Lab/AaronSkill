# canvas-kit

aw-canvas-design 的流程画布标准件，从一张已定稿的登录流程画布中抽出。新画布先复制这个目录，再填入流程数据：**视觉以 HTML 标准件为准，逻辑以 `reference/` 参考实现为准。**

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
3. **换成设计系统组件**：有 Sidebar、Dialog、Tooltip、Button 时，用它们搭出与标准件同等的效果，不自写树、弹窗和提示。例如 axo-ui 用 `SidebarTopbar`、`SidebarSectionHeader`、`SidebarItem` 按 Gallery 的组合搭目录（以 0.53.0 的实际导出为准：顶栏组件名是 `SidebarTopbar`）。
4. **填流程数据**：参照 `reference/flows.example.ts` 写流程，接好 `previewSrc` 与预览页的 `usePreviewBridge`。
5. **逐项对照**：打开对应 HTML 标准件与自己的画布并排比较，再按 SKILL 的验收矩阵检查。

## 参考实现（`reference/`）

此参考实现曾用 `react` / `react-dom` 19.3.0、`@xyflow/react` 12.11.6、`elkjs` 0.12.0 验证；这些版本不是目标项目的限制。`@phosphor-icons/react`（曾用 2.1.10）只是图标，可以换成项目图标。样式全部来自 `kit.css` 的类名。参考实现已用 TypeScript strict 模式通过类型检查，并实际打包运行验证：连线指标通过、拖动几何自检通过，info Dialog 显示在画布之上，悬停出口时出现临时去向线。

| 文件 | 职责 |
| --- | --- |
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
