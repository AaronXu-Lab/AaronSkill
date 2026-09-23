# Suggestion

Gallery ID: `suggestion` · 家族：建议操作

## Definition & Semantics

Suggestion 是由圆形缩略图和单行文案组成的紧凑建议操作。悬停时缩略图替换为调用方提供的操作图标；点击结果由调用方负责，不代表持久选中状态。

## When to Use

用户可以采用一个简短建议，且缩略图帮助识别该建议、图标表达采用动作时使用。通过原生 button 属性提供点击处理与禁用状态。

## When Not to Use

不要用它承载多行详情、持久单选或当前导航位置。普通提交、取消等不依赖缩略图的操作优先使用 Button。

## Similar & Easily Misused Components

- [Button](button.md) 承担通用操作；Suggestion 的识别来自缩略图与建议文案。
- [Item](item.md) 承载通用条目结构；Suggestion 是单个建议动作，不提供条目状态模型。

## Composition

### Recommended

放在相关输入或任务上下文附近，由调用方决定点击后填入内容还是执行操作，并提供必要反馈。

### Avoid

不要将另一按钮或链接嵌入 Suggestion；整行只有一个操作目标。不要仅通过悬停图标传达必须理解的动作含义。

## Internal Usage

imageSrc 提供静止时的圆形缩略图，icon 提供悬停替换图标，children 提供可理解的单行建议文案。图像与图标是装饰性媒体，不替代按钮的可访问名称；必要时由调用方提供 aria-label。没有内建选中状态，也不自行修改输入或提交请求。

## Examples

### Recommended

输入区域旁显示一个简短建议，点击后由调用方将对应内容填入草稿，用户继续编辑。

### Problematic

将多个 Suggestion 当作持久单选项，却没有提供选中语义或状态反馈；用户无法判断采用建议还是切换当前选择。
