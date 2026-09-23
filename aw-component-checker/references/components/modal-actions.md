# Modal Actions

Gallery ID：`modal-actions`。

## Definition & Semantics

Modal Actions 将一个模态任务的主操作、次操作和可选辅助内容组织为明确的操作区。组件表达操作之间的关系，不管理模态开合、业务提交或操作成功。

## When to Use

当模态任务需要统一完成、取消或有意义的替代路径时使用。存在独立帮助动作或选择数量等辅助信息时，可以使用辅助区，但辅助内容应服务同一任务。

## When Not to Use

不要把普通页面工具栏或任意并排按钮都包装成 Modal Actions。没有模态任务上下文时，固定的确认与取消结构会制造错误的提交边界。

## Similar & Easily Misused Components

- [Button](button.md) 触发单项操作；Modal Actions 组织一组任务操作。
- [Dialog](dialog.md) 和 [Dialog Basic](dialog-basic.md) 已通过结构化配置内部使用 Modal Actions；普通调用无需再手工重复提供。
- [Bulk Action Bar](bulk-action-bar.md) 对页面当前多选集合执行动作，不天然结束模态任务。

## Composition

### Recommended

在 [Sheet Basic](modal-panel.md) 的操作区使用 Modal Actions，或在 Dialog 的 customActions 中用于高级组合。次操作提供取消或另一条清楚路径，主操作提交当前任务，辅助区保留说明或帮助。

### Avoid

不要让辅助区也出现同等级的第二个“确认”，或让正文与页脚各自提交同一任务。多个次操作必须有不同的实际后果，不应只为了填满布局而保留重复退出入口。

## Internal Usage

主操作槽应只有一条明确的主要路径，次操作文字说明不同后果。auxText 应描述当前任务或选择范围，auxAction 应提供辅助动作。当前默认 Button 没有业务处理；Modal Actions 也不会替调用方关闭弹窗。

## Examples

### Recommended

资源选择任务的辅助区显示“已选择 3 项”，次操作取消，主操作“添加 3 项”提交相同集合。

### Problematic

辅助区显示“全部删除”，主操作为“继续”，两者后果互不相关却共享同一任务页脚。
