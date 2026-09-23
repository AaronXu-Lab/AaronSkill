# Ask User

Gallery ID: `ask-user` · 家族：Ask User

## Definition & Semantics

Ask User 是逐题收集用户补充信息的问答结构，在一组相关问题中呈现当前问题、答案选择和前进或提交路径。组件组织回答过程，回答产生的业务效果由调用方处理。

## When to Use

当前任务缺少有限而具体的信息，需要用户通过预设选项或自定义答案补充时使用。多题应服务于同一个待澄清任务，问题顺序应能被用户理解。

## When Not to Use

不要把 Ask User 当作任意操作菜单、长期设置页或无关问题的大型表单。当前实现允许未作答时继续或跳过，不应直接用于要求每题必答的流程；需要在执行前核对重大后果的任务，也不能把单选后的自动前进当成充分确认。

## Similar & Easily Misused Components

- [Composer](composer.md) 支持用户自行组织请求，Ask User 用有限问题补充已存在任务的信息。
- [Dialog](dialog.md) 聚焦一次独立决策或操作，Ask User 组织问题序列，本身不提供模态边界。
- [Ask User Option](ask-user-option.md) 是单个答案；Ask User 提供问题归属、选择模式和提交范围。
- [Message Answer](message-answer.md) 展示助手输出；嵌入 Ask User 时，回答收集仍是独立职责。

## Composition

### Recommended

在任务需要澄清的位置展示问题，将 Ask User Option 组织在对应题目下。

### Avoid

不要让 Ask User 的提交与相邻 Composer 的发送同时代表同一份待答信息，却维护两套答案。也不要在一个已有提交边界的表单内嵌入另一套独立问答表单，造成提交归属不清。

## Internal Usage

返回、继续、提交均作用于同一套问答状态；显示进度时，进度应描述题目位置而不是任务执行进度。

标题明确当前问题，选项共同回答该问题；单选或多选必须与问题允许的答案数量一致。关闭、跳过和提交是不同结果，调用方应明确关闭的业务含义。当前单选预设项会自动前进，用户应能理解这一流程；未答状态不能被记录为用户已经同意某个默认答案。

## Examples

### Recommended

任务开始前依次询问输出格式和材料范围，每题提供有限选项及其他回答，最终提交这组澄清信息。

### Problematic

问答卡选择“删除全部”后自动进入下一题，应用立即删除数据，却把普通选择当成执行确认。
