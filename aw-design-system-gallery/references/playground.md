# Playground 判断路由

目标是默认舞台、属性编辑与反馈共同正确。完整 Playground 检查覆盖以下三组；局部任务只读对应组，不默认扩大为全部 API 审查。

## 设计属性与排序

- 新增／删除轴、场景或改变 Caption 含义：读 [正式设计轴与场景](design-axes.md)。动画行为具有可感知差异时是正式设计轴，不能用终态截图相同排除。
- 新增或改名轴：在定义编辑器前读 [命名预检与映射](component-api-design.md#2-平台保留能力与映射)，确认设计名、代码名、值域和默认值；不因 API 未改变跳过。
- 属性顺序或 value 排序：读 [轴排序](property-model.md#轴排序) 或 [Value 排序](property-model.md#value-排序)，以及排序约定维护。仅排序不重选默认值、不改变属性契约。

## 默认与交互行为

- 默认组合选择：按工作流的证据优先级和 [默认与状态](component-api-design.md#3-默认与状态) 判断，明确设计推荐与运行时默认的关系。
- 动画、disabled 与适用条件：编辑后的预览必须反映真实组件行为；变化涉及适用条件时先读 [属性依赖与失效展示](property-model.md#属性依赖与失效展示)。区分组件本体的 disabled 与 Gallery 因前提失效而禁用控件，不相互替代。
- 事件效果：按 [交互归属](gallery-examples.md#交互归属) 区分真实组件行为与调用方效果，后者默认无副作用承接。
- 移除与空预览：按 [移除与空预览](gallery-page.md#移除与空预览)，组件真实消失，空预览由共享容器提供 Restore；不追加逐组件占位反馈。
- 重置：按 [Playground 重置](gallery-page.md#playground-重置) 同时恢复属性与主题覆写；前提切换保留原值。
- 验收切换属性后的真实结果、鼠标与键盘路径、状态反馈；动画比较观察实际触发过程。正式轴在 Properties 中共用定义和当前设置。

## 示例内容与舞台

先按 [实例数量](gallery-examples.md#实例数量) 核对默认单实例及多实例依据，再读 [可比较示例](gallery-examples.md#可比较示例)，核对通用 Text、描述角色 Description、图标 Placeholder、并列编号、字段与值层级、触发器与选项内容，以及选择后和 Reset 后的显示。边界提示涉及改动时再读该文件的范围提示小节；组合舞台涉及子组件时再读父子展示。

只为体验当前组合的交互可留在 Playground；需要独立展示时按 [Interactive Demo](component-sections.md#interactive-demo) 判断，不机械新增演示章节。
