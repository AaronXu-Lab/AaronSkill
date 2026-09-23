# Sonner

Gallery ID: `sonner`

## Definition & Semantics

Sonner 表示一次事件产生的短暂全局反馈，用户无需离开当前任务即可获知结果。通知可提供可选快捷操作，但不承担需要持续完成的任务界面。

## When to Use

结果不容易从当前界面直接感知，且简短说明足以完成告知时使用。结果已经明显呈现时，只有额外生效条件或撤销等有价值的后续行为才需要追加通知。

## When Not to Use

不要把必须修复的错误、表单校验的唯一说明或必须完成的后续操作放在会消失的 Sonner 中。不要每切换一次视图就报告成功。

## Similar & Easily Misused Components

- [Alert](alert.md) 保留与页面或对象相关的信息；Sonner 主要响应事件，显示时间结束后不应导致关键任务信息丢失。
- [Tooltip](tooltip.md) 解释一个目标，Sonner 报告一个事件。Tooltip 的出现不能作为操作成功的证据。
- [Spinner](spinner.md) 与 [Progress](progress.md) 表达进行中的任务，Sonner 不替代持续进度位置。

## Composition

### Recommended

通过应用已有的通知宿主提供统一反馈。需要撤销时，通过 `action` 配置提供指向同一次操作的快捷行动，组件内部使用 [Button](button.md)；调用方负责恢复逻辑。

### Avoid

不要为每个组件新增通知宿主，也不要把完整表单或多个不相关操作塞进通知。同一结果已经在触发控件内充分确认时，不再重复弹出等义提示；复制按钮反馈 Scenario 即为此类就地确认。

## Internal Usage

标题说明事件结果，说明文字只补充结果的必要条件。操作标签说明后续行为；“撤销”必须真正恢复对应操作。当前封装通过 `useToast().add` 提供通知，不应推断上游 Sonner 的全部 API 均由组件库公开。

## Examples

### Recommended

后台导出已完成时显示简短通知，结果仍可从原任务位置找到。

### Problematic

保存失败后仅显示短暂“失败”，没有字段反馈或持续恢复入口，通知消失后用户无法处理问题。
