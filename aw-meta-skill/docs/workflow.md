# AW Meta Skill 工作流

本文档是执行 AW Meta Skill 时优先读取的文本工作流，也是 `workflow.svg` 的语义事实源。SVG 仅是与本文档同步的可视化投影；若两者不一致，先依据 `SKILL.md` 修订本文档，再同步 SVG。

## 输入与产物

- 输入：创建或更新目标 SKILL 的请求、目标路径、用途与范围。
- 产物：符合 `skill-creator` 基础规范与 AW 附加契约的目标 SKILL，其中包含 metadata、`docs/workflow.md` 和 `docs/workflow.svg`，并通过基础校验与 AW 附加校验。

## 执行步骤

1. 接收请求并确认目标 SKILL 的路径、用途和修改范围。
2. 定位并完整读取当前环境中的 `skill-creator/SKILL.md`。
   - 若不可用：停止，报告基础 Skill 缺失，不凭记忆重建规则。
   - 若可用：继续执行。
3. 判断目标 SKILL 是否存在。
   - 新建：优先运行 `skill-creator` 的标准初始化器，建立 `SKILL.md`、UI metadata 与必要资源。
   - 更新：检查现有 `SKILL.md`、`agents/openai.yaml`、`docs/workflow.md`、`docs/workflow.svg`、脚本、引用资料和调用关系；保留范围外的字段、资源与策略。
4. 按用户真实用途与基础规范编写或修订目标 SKILL，保持描述可发现且具区分度，只增加确有必要的资源。
5. 维护 `metadata.version`、`metadata.author` 和 `metadata.creation_context`，按语义化版本规则决定版本变化。
6. 先创建或同步目标 SKILL 的 `docs/workflow.md`，确保文本独立描述主要阶段、关键判断、停止条件与最终产物。
7. 再依据 `workflow.md` 创建或同步 `docs/workflow.svg`，确保其可访问、可缩放、无远程依赖，并与文本工作流一致。
8. 运行 `skill-creator` 基础校验器和 AW 附加校验器；有脚本时运行最小相关测试，有 UI metadata 时核对其与 SKILL 的一致性。
9. 人工复核内容质量、版本合理性，以及 `SKILL.md`、`workflow.md`、`workflow.svg` 三者的语义一致性。
10. 报告目标路径、版本变化、metadata 取值、两种工作流文档状态和全部校验结果。

## 停止条件

- `skill-creator` 不可用时立即停止。
- 缺少会实质改变目标用途、授权范围或 author 身份的必要信息，且无法从可靠上下文推断时，停止并向用户确认。
- 基础校验、AW 附加校验或必要测试失败时，不得宣称交付完成；先修复，无法修复则报告具体阻塞。
