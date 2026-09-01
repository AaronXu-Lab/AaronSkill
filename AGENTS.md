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

## Skill 分类

新增或迁入一级目录的 Skill 时，必须读取其 `SKILL.md`，根据主要职责自动归入 README 的一个且仅一个分类。不要仅根据名称、依赖工具或次要能力判断；以触发场景、核心工作流和主要交付物为准。

按以下顺序判断，命中后停止：

1. **元 Skill**：主要交付物是另一个 Skill，或负责创建、升级、校验、打包和治理 Skill 本身。
2. **资源获取**：主要职责是从网站、应用商店、数据库、邮件或其他外部来源检索、验证、筛选和整理资源。即使后续包含轻量加工，只要获取与来源验证是核心，仍归入此类。
3. **设计 · Agent**：主要职责是对界面、体验、信息层级、视觉或 UI 文案作设计判断、审查和决策，并直接输出设计建议或修改结论。
4. **设计 · 支撑**：主要职责是为设计系统、设计规范、组件、Token、Gallery 或设计到代码流程提供基础设施、工程实现、验证和交付支撑。
5. **工具类**：不属于以上类别，且面向明确输入执行可复用的内容处理、资产加工、专项修复或个人生产力工作流。

如果一个 Skill 跨越多个分类，选择其不可替代的主要价值所在类别，并在 README 的“它解决什么问题”中说明其复合能力；不要重复列入多个分类。

## README 维护

- 每次新增、重命名、迁移或移除 Skill，都同步更新 `README.md` 的 Skills 区域及 Skill 总数。
- 活跃 Skill 必须出现在一个分类中，分类内按产品关系或工作流关系排列；没有明确关系时按目录名排序。
- 活跃分类表格沿用四列：`Skill`、`版本`、`它解决什么问题`、`关键边界`。描述和版本应来自 `SKILL.md`，不得凭目录名猜测。
- 已明确停止维护的 Skill 移入“不再维护”，不再出现在活跃分类中；除非用户明确要求，否则不要删除其目录。
- 新 Skill 无法可靠归类时，先根据上述判定顺序给出最合理分类；只有分类会实质改变仓库结构或发布策略时才向用户确认。

## 当前分类基线

- 元 Skill：`aw-meta-skill`
- 工具类：`aw-logo-asset-cook`、`aw-mail-read-later`、`rewrite-like-aaron`
- 资源获取：`aw-comic-dossier-packer`、`aw-logo-finder`
- 设计 · 支撑：`aw-design-md-author`、`aw-component-gallery-builder`、`aw-design-token-consistency-auditor`、`aw-find-and-port-ui-component`
- 设计 · Agent：`aw-ux-info-redundancy-audit`、`axo-wording-reviewer`
- 不再维护：`aw-figma-component-governance`
