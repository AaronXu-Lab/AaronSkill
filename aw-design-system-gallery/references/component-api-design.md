# 组件 API 设计约束

仅在 Gallery 审阅涉及组件契约、名称映射或 API 修改时读取。目标框架与项目约定优先。

## 1. 公开契约

- 公开 API 应表达消费方理解的稳定概念；不要为了排出整齐 Gallery 而制造轴或参数。
- 几何、视觉、内容、状态和行为尽量正交；存在真实依赖时明确父子关系。
- 互斥模式使用目标语言和框架适合的类型结构，避免允许冲突组合的多个开关。
- 内容通过目标框架惯用的 slot、内容入口或组合机制表达；样式扩展使用项目支持的机制。

## 2. 平台保留能力与映射

- 先确认实际宿主、目标框架的平台保留属性和值域，再判断 Gallery 名称是否冲突；不预设任何名称必须重命名。
- Gallery 名称与实现 API 不同时，比较语义、值域和转换，而非只看字面名称。
- 项目声明了映射配置时遵循；没有时仅记录当前组件的现场判断。可唯一确定的映射与真正歧义，按 [工作流的局部阻塞规则](../references/workflow.md#停止与局部阻塞) 处理，不因 Skill 示例修改 API。
- Gallery 展示模型保留设计值。默认值、属性轴、编辑控件、选项标签、Caption 与说明不得因为组件类型已改名而改用代码值；代码值只进入组件调用、类型检查和运行时分支。
- 在 Gallery 的渲染适配边界显式完成转换：可让 Gallery 状态持有设计值后转换为组件 props，也可让控件使用“设计 label + 代码 value”的成对选项。不要把存在映射的 Gallery 状态直接 spread 到组件，也不要依赖 `String(codeValue)` 自动生成用户可见文案。
- 代码 API 更新后，搜索旧值与新值在 Gallery 中的全部用途，分别核对默认编辑器、属性轴 Caption、Panel 描述、演示触发器和渲染调用。旧设计值仍可正确留在展示侧；新代码值只能留在适配侧。类型通过不能证明展示映射正确。
- 公开自定义参数的声明与实现读取顺序，可在不破坏类型继承、平台透传或运行时语义时尽量跟随 Gallery 的最终语义顺序。
- 组件 API、Gallery 轴与演示条件的区别，按 [正式展示与 Caption 规则](gallery-rules.md#2-选择设计审阅轴) 判断；不能为排版或填充 Caption 而新增组件参数。

### Gallery 到代码的命名

- 设计属性以已确认的 Gallery 最终名称、值域和语义为基准。代码名称仅为适配目标语言、框架原生能力或项目明确约定而映射，不另造一套设计概念。
- 在 JavaScript/TypeScript 中，组合值使用 lowerCamelCase：将表达组合关系的 `+`、`&` 转为词边界，保留各部分的顺序和数量；Gallery 继续使用便于设计阅读的原表达。

| Gallery 值 | JavaScript/TypeScript 值 |
| --- | --- |
| `icon+text` | `iconText` |
| `avatar+text` | `avatarText` |
| `title+description` | `titleDescription` |
| `+subtitle` | `withSubtitle` |
| `+description` | `withDescription` |
| `+icon&text` | `withIconText` |
| `+description&time` | `withDescriptionTime` |
| `+content` | `withContent` |
| `+footer` | `withFooter` |
| `+content&footer` | `withContentFooter` |
| `secondary+primary` | `secondaryPrimary` |
| `secondary+secondary+primary` | `secondarySecondaryPrimary` |

- 开头的 `+` 表达基于默认内容的追加时，代码值使用 `with` 前缀，后接 PascalCase 内容名，例如 `+subtitle` → `withSubtitle`、`+content&footer` → `withContentFooter`，保留原有累进渲染语义。没有前导 `+` 的组合仍使用普通 lowerCamelCase，例如 `icon+text` → `iconText`。若转换会造成同一值域内重名，或符号并非组合关系，先按语义消除歧义，不机械替换。
- 属性名映射须核查真实平台冲突。例如 React 的视觉 `style` 可映射为 `variant`；保留原生 `type` 的按钮／输入框，其内容类型可映射为 `contentType`；保留原生输入框 `size` 时，控件尺寸可映射为 `controlSize`。这些是有条件的映射，不要求无冲突组件统一改名。
- 状态轴可映射到框架惯用的 `checked`、组 `value` 等受控入口；内容仍通过独立 slot 或内容属性传入，避免为了名称一致而覆盖原生能力、吞掉内容或维护两套状态。
- 已授权实施 API 对齐时，在目标项目记录 Gallery → 最终代码契约的映射，同步类型、实现、Gallery 适配和实际调用；消费方迁移使用已实现并验证的最终契约。Skill 更新本身不代表已批准表中所有组件的 API 修改，也不授权发送消费方任务。

### 映射验收

- 从 Gallery 侧选择每个设计值，确认默认预览与属性轴渲染到对应代码分支。
- 检查默认值字段、选项标签、Caption 和描述中没有泄漏映射后的代码值。
- 检查组件调用中没有误传带 `+`、`&` 等设计符号的值；若组件契约本身明确使用这些符号，以真实 API 为准并记录该项目例外。
- 对可编辑默认值验证往返：切换值后展示标签仍是设计名称，重置后恢复设计默认值，组件收到对应代码值。

## 3. 默认与状态

- 默认值按 [工作流中的证据优先级](../references/workflow.md#2-按问题取证) 确定。
- Gallery 推荐组合不自动等于运行时默认；显式展示值应明确区分。
- 受控/非受控状态、事件和可访问性遵循目标框架惯例，不维护竞争状态或泄漏不稳定内部结构。
- 状态应暴露正确的平台语义；可见错误、忙碌、选中、展开或禁用状态不能只依赖颜色。

## 4. 修改边界

按 [工作流](../references/workflow.md#1-确定范围与模式) 核对修改授权；Gallery 审阅可报告 API 债务。实施 API 修改时，检查公开导出、类型、实现、受影响调用点与测试，并验证平台保留能力仍能正常透传。
