# 方法来源与取舍

创建或维护审查方法、需要追溯借鉴边界时读取；执行普通审计无需访问外部来源。以下是方法参考，目标 Skill 的实际规则以 `workflow.md` 为准；没有复制上游指令或代码，也不依赖安装这些 Skill。

| 来源 | 借鉴部分 | 本 Skill 的取舍 |
| --- | --- | --- |
| [magnus919/agent-skills · task-flows-and-state-models](https://github.com/magnus919/agent-skills/blob/main/product-design-and-ux/references/task-flows-and-state-models.md) 与 [状态模型模板](https://github.com/magnus919/agent-skills/blob/main/product-design-and-ux/templates/task-flow-state-model.md) | 从进入条件追踪到可观察结果；按业务条件判断状态适用性；覆盖跨角色交接 | 聚焦已有流程的完整性，不扩展为研究、信息架构或完整工程交付方法 |
| [product-on-purpose/pm-skills · deliver-edge-cases](https://github.com/product-on-purpose/pm-skills/blob/main/skills/deliver-edge-cases/SKILL.md) | 输入、边界、错误、并发与恢复；保留用户数据；按影响排序 | 同时审查正常路径，不强制填齐所有异常分类，不凭空估计发生概率 |
| [pbakaus/impeccable · harden](https://github.com/pbakaus/impeccable/blob/main/skill/reference/harden.md) | 网络、权限、重复操作、冲突与异常恢复的具体检查维度 | 只纳入影响流程连续性和结果的部分；不展开通用视觉、国际化、性能或安全审计 |

参考核对日期：2026-10-01。上游链接可能更新，变更本 Skill 前需重新核对相关内容；安装量或仓库受欢迎程度不作为设计规则的依据。

本 Skill 的额外约束来自用户确认的工作方式：已实现界面优先；未决业务规则主动提出方案；范围外环节记录依赖；审计报告交付后强制人工 Review，再依据审阅后的明确授权实施。
