# 方法来源与取舍

仅在维护 Skill 或需要核对参考方法时读取。本 Skill 独立编写，执行规则以 [workflow.md](workflow.md) 为准；以下资源作为方法参考，不是运行依赖，也不要求安装对应工具。参考内容于 2026-10-01 查阅，链接指向上游可变化的主分支。

## Cognitive Walkthrough

- 来源：[mastepanoski/claude-skills · cognitive-walkthrough](https://github.com/mastepanoski/claude-skills/blob/main/skills/cognitive-walkthrough/SKILL.md)。
- 借鉴：以具体任务为单位，检查步骤目标、操作可发现性、操作与目标的关联，以及进展反馈。
- 调整：从实际界面寻找路径后记录，不预先给出完整点击序列；把重复劳动与跨页面衔接纳入整体任务判断。用户知识由所选类型和事实定义。
- 不采用：无真实数据支持的用户成功率、改版收益预测，以及每个微小动作套完整长报告。

## Dogfood

- 来源：[vercel-labs/agent-browser · dogfood](https://github.com/vercel-labs/agent-browser/blob/main/skill-data/dogfood/SKILL.md)。
- 借鉴：界面操作为证据来源、问题即时记录、复现步骤关联截图或录像。
- 调整：使用目标环境可用的交互工具；按选定任务结束，不遍历全站或设问题配额。先保留首次尝试，复现后也不覆盖原始障碍。
- 不采用：绑定浏览器命令、每个交互问题强制录像、不可复现即不算问题等规则。

## 本 Skill 的独立约定

设计完成后使用独立新会话；允许完整读取 PRD，其他形式需求先澄清；由用户选定候选任务和用户类型，未另选类型时默认 A；必须操作可交互原型或产品；报告事实、影响及未决条件，先交人工 review，默认不提供具体修改方案。这些是本工作流的产品约定，不宣称为上述来源的共同要求。
