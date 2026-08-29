# AaronSkill 仓库规范

## 更新 Skill

- 每次修改任一 Skill 的指令、工作流、引用资料、脚本、测试或资源时，必须在同一次变更中主动更新该 Skill 的 `SKILL.md` 中的 `metadata.version`。
- Skill 保持工具和平台中立，不添加 `agents/openai.yaml` 或其他面向单一品牌、产品、模型供应商的专属 metadata 文件。
- 版本号使用语义化版本 `MAJOR.MINOR.PATCH`。更新现有 Skill 时默认提升 MINOR（`+0.1.0`）；明确的小改动提升 PATCH（`+0.0.1`）。
- 只有用户明确要求升级大版本号时才提升 MAJOR。遇到不兼容改动但用户未明确授权时，先停止并确认，不得自行升级 MAJOR。
- 每次版本号发生变化，都必须主动通知用户并报告“旧版本 → 新版本”，不得静默升级。
- 只修改仓库级文件且没有改变任何 Skill 时，不提升 Skill 版本。
- 版本变化后，同步更新根目录 `README.md` 的 Skill 版本列，确保它与 `SKILL.md` 一致。
- 工作流发生变化时，先更新 `docs/workflow.md`，再同步 `docs/workflow.svg` 和 `SKILL.md` 中的相关说明。
- 交付前同时运行 `skill-creator` 的基础校验器和 `aw-meta-skill/scripts/validate_aw_skill.py`，不得把校验失败的 Skill 标记为完成。
