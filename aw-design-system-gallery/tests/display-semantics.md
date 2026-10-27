# 展示语义回归（4.14.0）

仅供维护本 Skill 的展示标准及读取路由时使用。项目名和属性名是给定案例，不是通用组件例外清单；标准事实源为示例、Playground、章节和页面操作专题。走查结论不等同项目已修复或模型回放通过。

| 给定事实／请求 | 预期判断与九项归属 |
| --- | --- |
| Item 的 Properties 在目标最外层与内部包装同时出现辅助 Bounds。 | Properties 的边界提示不通过；目标仅最外层一层，去掉示例包装或内部重复辅助线，不能删除真实组件边框。 |
| 一个必要组合中有两个明确被审阅的目标实例。 | 每个实例各自一层 Bounds；不强制整组共用一个大框，也不继续标内部布局和复用子组件。 |
| 关闭 Bounds 后真实边框仍可见。 | 正常；区别真实组件表面与辅助线，既有开关及 Portal 规则继续适用。 |
| Item Section Group 在 Playground 或 Properties 被随意窄包装限制宽度。 | 按职责占满可用宽度；各比较实例各自行宽，不从包装宽度反推组件设计。 |
| 另一个紧凑组件按职责自适应，另一个固定宽度实例处在窄容器。 | 不机械改为占满；固定宽度仍检查有效尺寸和防溢出，不能以宽度规定覆盖真实契约。 |
| Item Surface 采用固定宽度，却在 Properties 横向挤成一组。 | 宽度可保留，但排列改为纵向每行一个；宽度和排列分开判断。 |
| Pagination 的 range／simple 实例横排，相邻按钮易误读为同一翻页组。 | Properties 纵向每行一个，保持实例边界与比较关系清楚，不修改组件内部按钮布局。 |
| 固定宽度的其他实例横排并自动换行，间距、顺序及实例身份清楚。 | 可保留；不能把上述纵排案例推广为所有固定宽度组件必须纵排，也不一概禁止 flex 自动换行。 |
| Markdown 的 Interactive Demo 同时堆放 Edit、Mermaid 流式及异常源码展示。 | Markdown 仅保留核心 Edit；Mermaid 专属演示归 Mermaid，再按其核心 UX 和正式展示筛选判断，不因支持子组件就收纳所有演示。 |
| Menu 的 Interactive Demo 同时包含开关、键盘、子菜单、空间不足的核心切换，以及 @ 引用编辑器、对齐、Undo/Redo 综合流程。 | 保留前四类 Menu 核心 UX，后者归对应组件或组合／Scenario；不把全部集成用例留在 Menu，也不禁止必要的最小上下文。 |
| Progress Anatomy 的 Element 为 Track and indicator；Property 为 Trailing content。 | 按稳定职责分别概括为 Progress bar、Trailing，形态和行为放 Description；不按图形或渲染分支罗列。 |
| 另一个组件同时有职责不同、需要独立解释的两个自身部位。 | 分别命名，不为避免 and／斜杠或追求短名把真正不同的部位硬合并。 |
| Stat Cards Group 没有可调设计属性，却保留空白侧栏。项目 DS Playground 支持 adjuster: "float"。 | Playground 应使用当地浮动工具栏方式，案例映射为 adjuster: "float"；通用规则不强制所有平台提供同名 API。 |
| 有设计属性，但当前模式使所有依赖控件暂时失效。 | 不属于无属性组件，保留依赖控件、禁用原因和用户值，不改成无属性侧栏方案。 |
| Sidebar Item Meta 是紧凑目标，外层满宽包装居中而实际目标靠左。 | Playground 不通过，应让实际组件水平、垂直居中；不能只证明包装居中。组件内部文字对齐不因此改变。 |
| 目标组件本来占满宽度，或具有明确布局职责。 | 按职责保留宽度与相应对齐，不为居中缩窄或强改内部布局；Properties 排列独立判断。 |
| Composer Attachment 刷新时 Restore 短暂闪现，随后正常内容出现。 | Playground 空预览状态判定不通过；初始化／挂载／加载／正常入场不等于确认空。检查首次加载与刷新过程，源码不足时最小浏览器复核，不用稳定截图证明无闪现。 |
| 用固定延时隐藏 Restore，或永久关闭 Restore，以消除上述闪现。 | 不通过；应依据内容就绪／确认无内容的状态，真正空预览或已移除仍提供共享唯一 Restore。保留设置、重复移除／恢复与 Reset 职责不变。 |

维护者走查：工作流 → 既有九项对应入口 → 目标单层 Bounds、宽度／对齐／排列、核心 Demo、Anatomy 命名、无属性工具栏与 Restore 生命周期的细则及验收。检查正例、反例和局部改动路径，避免扩大为全组件浏览器巡检。

未将 Lightbox loading 统一、Input shape/circle 删除或 Lightbox 导航归组纳入本次标准；它们不是本任务的 Skill 变更范围。保留九项矩阵、源码优先、Description 许可、关联覆盖排除、动画轴、默认无副作用示例及共享 Restore。本记录为文档语义走查，未进行独立模型回放或 AaronUI-Web UI 测试。

## 任意自定义内容插槽（4.15.0）

| 给定事实／请求 | 预期判断与九项归属 |
| --- | --- |
| Message Activity 的 content="custom" 在 Playground／Properties 中放入另一个 Message Activity。 | 对应展示项不通过；改用既有内容占位组件，显示英文 Content 加虚线边框。真实嵌套保留在明确的场景 Example。 |
| Section Header 的任意内容区域使用 ContentPlaceholder，显示 Content 与虚线。 | 可复用当地占位；48px 只是该项目实例取值，不提升为通用固定高度或公开 API。 |
| 一个组件的任意自定义插槽位于多个属性比较实例内。 | 各实例复用一致的 Content 虚线占位；只覆写被比较轴，不按 value 填入不同业务组合。 |
| 组件具有 label、description、icon 等专用插槽。 | 沿用 Text、Description、Placeholder 或已有明确语义；不能因它们也由调用方传入就统一替换为 Content。 |
| 明确的场景 Example 需要展示三层嵌套。 | 保留真实组合及层级，不把场景也改成 Content；不把场景反向塞回组件通用 custom 比较。 |
| 占位虚线与目标组件 Bounds 同时存在。 | 按项目区分插槽占位识别边界与目标最外层辅助线；复用既有机制，不重复注册占位为额外目标，也不为消除重复 Bounds 删除占位含义。 |

维护者沿工作流的占位判断入口走查上述六例，核对规则适用边界、默认／比较一致性、场景归属及项目尺寸边界。本次为文档语义走查，未进行独立模型回放或新增 Gallery UI 修改。
