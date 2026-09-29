# 属性依赖路由回归

仅在维护本 Skill 的触发入口、依赖规则或工作流时使用。以下是测试输入与判定依据，不是另一份正式展示规则；规则事实源为 [§3](../references/gallery-rules.md#属性依赖与失效展示)。可由维护者逐项走查，或在隔离样例中回放模型执行；报告必须区分两者，不以文本关键词匹配声称行为通过。

## 核心事故场景

请求：“Input Area 的 ghost 模式不支持 draggable，请同步组件和已有 Gallery。”

给定：组件有 solid 与 ghost 两个模式；solid 支持 draggable；Gallery 有共享 Default 配置控件和 Properties 比较块；当前用户设置 solid、draggable=true；文档版式以 Playground 承载 Default 编辑器，两处共用属性轴定义。

判定：从入口路由到 §3，修改前识别 mode → draggable；区分本体手柄与 Gallery 配置和比较轴；方案及验收完整覆盖 §3，不把组件隐藏手柄扩展为删除配置或比较轴，只对失效的 Playground 依赖控件与 Properties 比较块应用灰化、inert 和外层 Tooltip；两处共用 disabledReason，提示满足统一格式，不包含 Default。无关控件保持可用。切到 ghost 再回 solid，draggable=true 不丢失；测试鼠标、键盘、外层提示与显式重置。仅提供截图不能判定交互验收通过。

## 相邻与反例

| 测试请求 | 应选择的路径与判定 |
| --- | --- |
| “新增 selectable，仅在 selectionMode=multiple 下生效，更新 Gallery。” | 识别新增依赖，读 §3；新增轴还读 §2；不需要通读其他章节。 |
| “把这个 Gallery 子属性改成条件展示，前提不满足时隐藏。” | 读 §3 并辨认用户明确要求与默认保留规则的差异；按有效用户要求处理，说明差异，不静默套用默认规则。 |
| “只调整既有 Gallery 尺寸轴顺序。” | 读 §3 的排序规则，无需重选场景或运行无关依赖验收。 |
| “只把 Gallery 默认占位文本换成 Text。” | 读 §6，不因文件中存在依赖规则而增加 §3 全套验证。 |
| “修改业务表单权限条件，不涉及 Gallery。” | 不触发本 Skill。 |

## 文档版式相邻场景

| 测试请求 | 应选择的路径与判定 |
| --- | --- |
| “把 Panel 改成文档版式。” | 读 §3 Panel 内容结构；四个 Section 按约定排列，Playground 与 Properties 共享轴序和取值。 |
| “属性没改，只切换预览主题后 Reset 仍不可用。” | 读 §3 Playground 重置；主题覆写计入修改，Reset 恢复属性默认值和 Follow Gallery；无需重新筛选轴。 |
| “Properties 标题增加复制链接及背景菜单。” | 读 §3 Section 头部与深链；复制 Section 链接并短暂反馈，link 右侧复用原 Panel 菜单。 |
| “直接打开 button 的 properties 链接没有定位，同页换 hash 也无效。” | 读 §3 深链规则；路径识别页面，hash 识别 Section，首次打开和同页切换均滚动；不恢复 hash 页面路由。 |

## 本次维护走查记录

4.0.0：维护者逐项追踪入口 → 工作流 → §3 规则与验收。依赖场景覆盖两处共享禁用与值保留；文档版式、仅主题覆写、Section 操作与两种深链进入对应小节。局部排序和文案请求仍按需读取，业务表单反例不触发。

这是文档语义走查，未运行独立模型回放或真实项目 UI 交互测试，不能证明未来模型必然执行，也不代表事故项目已修复。
