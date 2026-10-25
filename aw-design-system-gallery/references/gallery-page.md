# Gallery 页面与操作

Components 页面结构、MDX、Playground 重置及共享 Section 操作按对应小节读取；其他章节判断由 Components 九项入口路由。

### 组件页面内容结构

新增组件页面，或实质调整现有页面的示例结构时，先查目标项目当前的页面结构与共享内容适配器。若当地已定义文档版式或旧版 Default／Properties／Demo 等固定组合，复用仍有效的共享适配器；旧版代码概念与用户可见名称按下述映射处理。不要恢复已移除的 Panel 外壳，也不要把旧式 Example 卡片排版当作当前页面标准。分类通常不改变页面结构；Temporary 可按下述条件精简，其他例外必须由目标项目的明确约定支持。

Components 页面的章节按以下顺序组织，不增加单独的 API Props 章节或表格；公开 API 由代码契约维护，页面的 Properties 只解释可审阅的设计属性：

1. **Playground** 必有，承载默认示例与可编辑属性。
2. **Anatomy** 可选，仅在组件自身拥有值得说明的可视构成时出现；具体按 [Anatomy 标准](component-sections.md#anatomy) 判断。
3. **Interactive Demo** 仅在需要独立交互体验时出现，按 [演示标准](component-sections.md#interactive-demo) 判断。
4. **Properties** 仅在有正式设计属性轴时出现，其轴、值和顺序与 Playground 的编辑项对应，两处共享状态。
5. **Usage** 必有，说明何时使用该组件。
6. **Composition** 仅在需要说明与关联组件的组合用法时出现。
7. **Best Practices** 仅在有具体使用规则时出现。

Temporary 中的组件为了快速迭代，可以只保留 Playground；增加其他章节时仍遵守上述顺序和出现条件。需要交互才能理解的行为可在 Playground、对应 Properties 示例或满足出现条件的 Interactive Demo 中展示，避免重复演示。迁移已有独立章节时保留稳定页面 ID 与锚点，不为整理目录而丢失必要交互。

目标项目明确规定 Internal 分类仅展示 Playground 时，该分类的每个组件页面只保留一个可见 Playground，不另列 Anatomy、Properties、Usage、Composition、Best Practices 或 Interactive Demo。仍复用当地 Playground 内容适配器，所需设置留在这个 Playground 内；文档、翻译或内部事实源可保留供其他用途，但不能把多余章节投影到页面。此例外只适用于项目明确声明的 Internal 分类，不从分类名称自行推断。

- Playground 是 Default 编辑器的用户可见名称；Default 仅作代码内部概念，不向用户展示。它用当地标准编辑器承载当前默认值，并在同一个默认舞台渲染结果；默认设置与后续属性对比共享状态。
- Properties 按正式设计轴逐项展示 Caption 与比较舞台，每项只覆写正在比较的轴，并继承当前 Playground 的其他值；两处使用同一份轴顺序，不分别维护顺序表。
- 文档版式按上述章节顺序组织；复用当地共享文档结构，省略不适用的可选章节。
- 交互演示沿用当前 Playground 设置，不把触发方式伪装成属性轴。
- 没有正式展示轴时仍使用当地标准的单一 Playground 编辑器结构，省略空 Controls、Properties 与空 Caption；不要退回旧的独立 Example 卡片排版。

MDX 校验核对 frontmatter（若使用）、共享布局与示例引用／导入、标题和章节顺序、代码围栏、组件标签及参数、链接与锚点；以实际项目语法为准。检查编译及页面渲染，不以 MDX 能编译代替内容或交互正确。项目未采用 MDX 时检查其等价页面源。已有链接按所在内容核对目标与锚点；不检查关联覆盖或要求补卡片。

验收时把目标页面与当地现行页面结构核对：标题层级、Controls、舞台、Caption 位置、区块间距和共享状态必须属于同一内容模型。仅让示例“看起来接近”或保留相同边框，不算复用标准结构。

组件没有适合矩阵展示的设计轴时，仍保留一个有意义的 default 示例和 Gallery 自己的 line-light 舞台边框，但省略 default Caption 整行，不渲染空 Caption。没有展示轴不自动意味着组件属于 Temporary；分类应依据目标项目的独立标准判断。

### Playground 重置

Reset 仅在存在非默认值时可用：组件设置偏离默认值，或预览主题选择了 Follow Gallery 以外的覆写，任一成立即启用。点击 Reset 同时恢复组件默认值与 Follow Gallery；全部恢复后按钮禁用。仅切换属性依赖前提不能清空用户值。

验收默认状态、仅属性修改、仅主题覆写、两者同时修改及重置后状态；不能只用组件属性是否改变判断 Reset。

### 移除与空预览

组件支持移除、关闭或删除自身展示时，示例应执行真实移除。不要在组件原位置追加 Removed、已移除、操作成功等占位反馈，也不要由各组件示例自行补 Restore 按钮；有其他示例内容时直接保留剩余内容。

Playground 的整个预览区没有组件内容时，由共享展示容器提供唯一的 Restore 入口，采用标准 icon+text、outline 按钮，不附加说明或成功文案。空预览判断依据实际渲染结果，覆盖返回 null、空 Fragment 及无内容的布局 wrapper；容器本身的边框、辅助范围提示与恢复按钮不算示例内容。仍存在文字、图标、媒体、控件或组件自身的可视表面时，不显示空预览入口。

Restore 恢复被移除的预览内容，保留当前设计属性和预览设置；顶部 Reset 仍按其既有契约恢复默认值。两者复用项目共享状态与恢复机制，不制造组件公开属性或新设计轴。Gallery 容器的 Restore 文案属于网站界面，按项目语言约定翻译。

验收移除后没有残留占位反馈、空预览仅有一个标准恢复入口、恢复后保留当前设置，以及重复移除／恢复与键盘可达性；局部内容移除但预览非空时不显示恢复入口。已采用共享容器的页面、小窗口和主题继续遵循当地展示约定。

### Section 头部与深链

- hover Section 标题时显示 copy link 图标按钮；键盘聚焦也应能发现并操作该按钮。点击复制指向当前 Section 的链接，复制成功后短暂显示已复制状态，再恢复；复制失败不得显示成功。
- 需要 Section 菜单时，在该 Section 标题的 link 按钮右侧使用项目现有的 Section 菜单与 Block Background 等能力，不恢复旧版 Panel 菜单，也不另造一套菜单状态。
- 页面使用路径路由，如 `/components/button`；`#` 只用于页内定位，如 `/components/button#properties`，不再使用 `#/components/button` 形式。侧边栏、复制链接与页内导航使用同一套路由和稳定 Section ID。
- 首次打开带 hash 的链接，以及同页切换 hash 时，均在目标 Section 可用后滚动到它；不能只在首次挂载时处理。页面直接打开或刷新也应能解析路径。

验收 hover／键盘操作、复制内容与短暂反馈、受影响 Section 菜单的顺序与功能，以及深链首次打开、刷新和同页 hash 切换。分类迁移继续遵守 [稳定标识要求](gallery-navigation.md)。


