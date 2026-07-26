---
name: aw-figma-component-governance
description: 在审查、创建或调整 Figma 设计系统组件、ComponentSet、Variant、组件属性、Slot 和内部图层命名时，应用这套 Figma 组件库规则。适用于整理或排序 ComponentSet 的 Variant/Variant value、报告需要手动拖拽的 Figma values、让 Figma 组件符合组件库规则、补充 Variant、重命名属性/图层、判断 Variant 与 Property 边界，或创建 UIKit/PC 组件。
metadata:
  author: aaron_xu
  version: "0.2"
  creation_context: "为沉淀个人 Figma 组件库的命名、Variant 排序、Property/Slot 建模和人工调整规则而创建，减少组件治理中的重复判断。"
---

# Wallys Component Maker

在这个设计库中处理 Figma 组件时，使用以下规则。优先采用小步、增量的 Figma API 读取和写入，并在每次有意义的改动后进行校验。

## 工作流

1. 编辑前先检查目标节点：组件名、组件集属性、Variant、文本/布尔/实例替换属性、直接子图层和内部图层命名。
2. 应用下方命名和结构规则。除非用户明确要求视觉重设计，否则保留现有视觉样式。
3. 谨慎选择 Variant 或 Property。若 Boolean Property 足以表达可选内部内容，避免扩张 Variant 数量。
4. 编辑后进行校验：组件/属性/Variant 命名、图层命名、属性引用、Auto Layout 尺寸，以及预期 Variant 数量。

## 组件结构

- 基础组件视为不可拆分的原子组件，例如 `Button`、`Checkbox`。
- 复合组件视为多个基础组件的组合，例如 `Dialog`、`Modal`、表格相关组件。
- 仅在确实有帮助时使用内部辅助组件。私有/内部组件使用 `_` 前缀，例如 `_Table / Resize Handle`。

## 组件命名

- 组件名使用首字母大写，多个单词用空格分隔：`Navigation Bar`。
- 组件族使用 ` / ` 分隔：`Table / Header`、`Menu / Item`。
- 私有组件族结合 `_` 和带空格的斜杠：使用 `_Modal / Header`，不要使用 `_Modal/Header`。
- 移除默认名或占位名，例如 `Frame 185`、`Property 1=Default`、`Variant2`。

## 图层命名

- 图层名使用首字母大写：`Content`、`Leading Icon`、`Description`。
- 优先使用单个英文单词；如果必须多个单词，用空格分隔。
- 使用语义命名，不使用形状命名。
- 优先使用位置/职责类命名：`Leading Icon`、`Trailing Icon`、`Header`、`Footer`、`Body`。
- 优先使用内容/职责类命名：`Label`、`Title`、`Description`、`Helper Text`、`Value`、`Texts`。
- 可替换内容尽量和 Property 对齐。如果属性叫 `icon`，图层尽量叫 `Icon`；如果属性叫 `text`，图层可叫 `Text` 或更语义化的 `Label`。
- 组件自己的图层不要保留默认名，例如 `Frame 123`、`Group 9`、`Rectangle 2`、`Vector`。外部图标/组件实例内部继承来的图层可以忽略，除非正在编辑该源组件。
- 私有辅助图层使用 `_` 前缀，例如 `_Measurement`、`_Touch Area`、`_Mask`。
- Slot 命名为 `Slot` 或按职责命名：`Leading Slot`、`Content Slot`、`Trailing Slot`。
- Figma 会将 Slot Property 名和 Slot 图层名耦合。当这种耦合导致属性命名规则与可见图层命名规则冲突时，优先满足图层名：保留 Title Case 的 Slot 显示名/图层名，例如 `Content Slot`、`Trailing Slot`。

## Variant 规则

- Variant 的属性名使用 lowerCamel：`showClear`、`showHeader`、`isOn`。
- Variant 的值使用 lowercase。若需要多个单词，用空格分隔：`input text`、`close only`、`variable set`。
- Boolean Variant 的值必须是 `false` 和 `true`。
- 统一用词：使用 `trailing`，不要使用 `tail`。
- Variant 值必须有语义。把 `align4`、`Variant2`、`Default` 等生成值替换成有意义的值。

## Variant 排序规则

整理现有组件集时，先保留当前 Figma Page 中的组件集顺序，再按以下规则排序 Variant 名和值。

### Variant Name 顺序

Variant Name 的排序遵循：

1. 布局结构优先于视觉状态。
2. 对布局结构影响越大的越靠前。
3. 对视觉状态影响越大的越靠前。
4. 枚举优先于布尔。

常见 Variant Name 优先级：

`size > style > type > width > content > trailing > position > align > count > selection > state > showClear > showHeader > selected > toggled > check > disable`

可以直接根据实际存在的值过滤输出。未列出的 Variant Name，按上述通用原则判断排序。

### Variant Values 顺序

Variant Values 分为枚举、布尔和数字。

枚举值排序遵循：

1. 若存在 `none`，`none` 放最前，表示无内容/无附加能力的基础状态。
2. 常规值优先于特殊语义值，例如 `destructive` 放在常规样式之后。
3. 内容类枚举中，纯文本优先于非文本内容。
4. 内容类枚举中，单值优先于组合值。
5. 视觉样式类枚举中，从轻到重排序。
6. Size 类枚举属于布局尺度，按从大到小排序，不跟随视觉样式从轻到重的规则。
7. 方位类枚举按方位规则排序。
8. 参考顺序可以直接根据实际存在的值过滤输出；未覆盖的值按语义接近原则插入。

参考顺序：

- `style = ghost, tint, underline, outline, block, light, bordered, fill, destructive`
- `size = large, medium, small`
- `type = text, symbol, icon, symbol+text, icon+text`
- `state = default, normal, hover, activate, active, loading, success, warning, error, disable`
- `position = top, left, right, bottom`

数字按从小到大排序。布尔值按 `false, true` 排序。

### Figma API 限制与手动拖拽清单

Figma Plugin API 会通过 `componentPropertyDefinitions` 暴露 `variantOptions`，但公开 API 没有提供安全的原地重排现有组件集 Variant Values 的方法。API 可以通过重写子 Variant Component 名称来安全调整 Variant Name 顺序，但 Variant Values 的下拉顺序可能需要在 Figma 右侧面板中手动拖拽。

当用户要求整理 Figma 中的 ComponentSet Variant 时：

1. 先执行所有安全的 API 调整，尤其是 Variant Name 顺序。
2. 除非用户明确接受组件身份、发布关系和现有实例引用风险，不要为了重排 Variant Values 而重建现有 ComponentSet。
3. 额外返回一个“需要手动拖拽的 Values”部分，列出所有当前顺序与目标顺序不一致的 ComponentSet / Variant，并给出当前顺序和目标顺序。
4. 说明这些条目需要手动拖拽，是因为公开 Figma Plugin API 不能安全地原地重排 `variantOptions`。

## Property 规则

- Property 名使用小写或 lowerCamel：`text`、`showTrailing`。
- 主文本统一使用 `text`。
- 多文本场景使用语义字段，例如 `title`、`description`、`label`、`detail`。
- Text Property 的默认值应和属性名对应，并使用首字母大写：`text` -> `Text`，`helperText` -> `Helper Text`。
- 可选内容使用 Boolean Property，并统一命名为 `show...`，例如 `showDescription`、`showTrailing`。
- 可替换图标或符号使用 Instance Swap Property；图层命名与属性对齐，例如 `Icon`。

## Variant 与 Property 的边界

- 当某个选择会改变组件核心结构、布局类型或状态矩阵时，使用 Variant。
- 当某个选择只是控制内部可选元素显隐时，使用 Boolean Property。
- 如果 Property 能表达同样控制，并且不会隐藏结构含义，优先减少 Variant 数量。
- 示例：`Empty` 组件中，`actions=none|primary|primary+secondary` 适合用 Variant；可选说明文本适合用 `showDescription` Boolean Property。

## Slot

- 当组件内部包含使用者需要动态替换的灵活内容时，使用 Slot。
- 对于 Modal、Menu、内容容器等复合组件，如果固定的文本/图标属性过于限制，应使用 Slot。

## Figma 实操注意事项

- Variant 定义只从 `ComponentSetNode.componentPropertyDefinitions` 读取。单个 Variant `ComponentNode` 不暴露 Variant 定义，只暴露自身当前的 `variantProperties`。如果只读脚本在单个 Variant 上读取失败，改为限定在所属 ComponentSet 上读取后继续。
- 编辑文本或文本绑定属性前，先加载字体。如果组件包含混合字体或不可用字体，必要时先用 Inter 作为临时默认字体，再在最后统一加载原字体并重新应用文本样式或字体变量。
- 写入前优先做只读检查。返回 ComponentSet ID、子 Variant ID、当前 `componentPropertyDefinitions` 和当前子组件名称，方便后续写入稳定定位。
- Figma 写入保持小步、窄范围。先通过重命名子 Variant Component 调整 Variant Name 顺序，再校验 definitions，然后再考虑其他改动。
- 除非用户明确接受风险，不要用破坏性重建来修复顺序。重建 ComponentSet 可能改变组件身份、发布关系和实例引用。
