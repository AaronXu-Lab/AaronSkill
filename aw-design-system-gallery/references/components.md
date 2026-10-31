# Components 九项标准

按组件页面的检查顺序组织，目标是展示正确且开发契约一致。先判断本次涉及哪些项，再展开链接；完整校验逐组件覆盖九项，局部任务无需通读全部细则。九项是检查维度，第 3 项不要求新增页面章节。

| 检查项 | 判断目标与按需读取 |
| --- | --- |
| 1. 页面结构／MDX | 页面结构、章节条件、MDX 格式和引用正确。读 [页面结构](gallery-page.md#组件页面内容结构)；菜单和深链变化再读其操作小节。 |
| 2. Playground | 当前默认组合能被正确展示和编辑，核对实例数量、目标宽度与居中、无属性工具栏及事件归属。进入 [Playground 判断路由](playground.md)，按属性、默认与行为、内容展开。 |
| 3. 代码与开发契约 | 开发调用满足一致标准；核对设计属性默认值与组件运行时默认值的一致性。读 [代码检查路由](component-api-design.md#代码检查路由)，覆盖页面名与真实组件调用名的对应关系、可调用属性、映射、默认值、原生能力、父子依赖与健壮性；按实际问题展开。 |
| 4. Anatomy | 可选；先判断组件自身是否拥有值得说明的可视部位，再核对稳定部位抽象、简短名称、层级和直白说明。读 [Anatomy](component-sections.md#anatomy)。 |
| 5. Interactive Demo | 可选；只演示当前组件核心 UX，保留必要的最小上下文，以统一方式体验。读 [Interactive Demo](component-sections.md#interactive-demo)。 |
| 6. Properties | 每个 value 默认单实例，与正式设计属性对应；每个实例只覆写当前轴，其余跟随 Playground，宽度与排列独立判断。读 [Properties](component-sections.md#properties)，再按改动进入属性、顺序或依赖细则。 |
| 7. Usage | 格式正确，说明何时、为何以及如何使用。读 [Usage](component-sections.md#usage)。 |
| 8. Composition | 关联组件的常见组合足够、真实且分工清楚。读 [Composition](component-sections.md#composition)。 |
| 9. Best Practices | 建议具体、正确且可执行。读 [Best Practices](component-sections.md#best-practices)。 |

仅分类迁移时读 [分类与稳定标识](gallery-navigation.md)，组件身份改名进入第 3 项。各项验收就近维护；实施时按 [验证与恢复](verification.md) 选择受影响检查。校验结果按 [统一报告](audit-report.md) 展示。

不做全站关联覆盖普查；已有文章关联的目标、呈现方式及已知独立 Example 的关联入口归第 1 项，按 [关联文章](gallery-page.md#关联文章) 检查。完整案例误放 Composition 归第 8 项。
