<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="AaronSkill：一组可直接安装的实用 Agent Skills">
</p>

<p align="center">
  <strong>把真实工作流封装成可发现、可验证、可复用的 Agent Skills。</strong>
</p>

<p align="center">
  Skill 工程 · 设计系统 · UI/UX 审计 · 品牌资产 · 阅读助手 · 内容生产
</p>

## 一条命令安装

```bash
npx skills@latest add AaronXu-Lab/AaronSkill
```

安装器会发现仓库中所有包含 `SKILL.md` 的技能，并让你选择需要安装的项目。只查看可用技能：

```bash
npx skills@latest add AaronXu-Lab/AaronSkill --list
```

安装单个技能：

```bash
npx skills@latest add AaronXu-Lab/AaronSkill \
  --skill aw-find-and-port-ui-component
```

全局安装到 Codex：

```bash
npx skills@latest add AaronXu-Lab/AaronSkill \
  --skill aw-find-and-port-ui-component \
  --agent codex \
  --global
```

> `skills` CLI 默认在项目范围安装；添加 `--global` 可供所有项目使用。交互式安装默认推荐软链，使用 `--copy` 才会创建独立副本。

## Skills

| Skill | 它解决什么问题 | 关键边界 |
| --- | --- | --- |
| [`aw-design-md-author`](./aw-design-md-author/) | 按 Google Labs 规范创建、审查和维护完整的 `DESIGN.md` 视觉契约 | 必须完成官方 lint；不代替代码或 Figma |
| [`aw-design-token-consistency-auditor`](./aw-design-token-consistency-auditor/) | 比较 Figma Variables、`DESIGN.md` 和 CSS/Less Token | 只生成审计证据，不自动改写 Token |
| [`aw-figma-component-governance`](./aw-figma-component-governance/) | 治理 Figma 组件命名、Variant、Property、Slot 和顺序 | 不安全的 Variant 值重排保留为人工操作 |
| [`aw-find-and-port-ui-component`](./aw-find-and-port-ui-component/) | 搜索、验证并移植 UI 组件实现 | Find 与 Port 严格分阶段，必须由用户明确选择 |
| [`aw-logo-asset-cook`](./aw-logo-asset-cook/) | 从唯一 SVG 事实源生成并验证 Web、桌面端与移动端全平台图标资源 | 必须由用户明确指定源文件或目录；单主题补色与清理产物前需要授权 |
| [`aw-logo-finder`](./aw-logo-finder/) | 从官网、Logo 资源站和应用商店寻找、比对并导出品牌或产品 Logo | 必须先确认候选与输出尺寸，再生成无损 WebP |
| [`aw-mail-read-later`](./aw-mail-read-later/) | 从 Outlook 的 `Read Later` 文件夹推荐、阅读、总结或翻译一项内容 | 手动一次处理一项；归档或移除邮件前必须得到用户确认 |
| [`aw-meta-skill`](./aw-meta-skill/) | 基于 `skill-creator` 创建或更新符合 AW 交付规范的 Skill | 必须维护版本元数据与 `docs/workflow.svg`，并通过基础及附加校验 |
| [`aw-ux-info-redundancy-audit`](./aw-ux-info-redundancy-audit/) | 审计 Web 界面的语义重复、信息密度和层级问题 | 先输出审计证据与最小改动决策，再实施界面修改 |
| [`aw-comic-dossier-packer`](./aw-comic-dossier-packer/) | 收集漫画封面、整理来源介绍、生成小红书封面与最终档案 | 高清化需确认费用；社媒图使用原创视觉而非复刻封面 |
| [`rewrite-like-aaron`](./rewrite-like-aaron/) | 将 AI 中文草稿改写为 Aaron 当前的博客文风 | 保留事实与立场；限制口头禅、反问和中英混写的表面模仿 |

## 这些 Skill 如何工作

```text
真实需求
   │
   ├─ 读取项目、来源与环境约束
   │
   ├─ 执行窄范围、可追溯的工作流
   │
   ├─ 在高风险或高成本动作前停下确认
   │
   └─ 用 lint、结构化报告或结果回读完成验证
```

仓库里的 Skill 倾向于把脆弱、重复的步骤放进 `scripts/`，把规则和 schema 放进 `references/`，并让 `SKILL.md` 保持为清晰的执行入口。

## 仓库结构

```text
<skill-name>/
├── SKILL.md              # 触发说明与完整工作流
├── agents/
│   └── openai.yaml       # Agent UI metadata
├── scripts/              # 可重复执行的确定性工具（按需）
├── references/           # schema、规范与运行手册（按需）
└── fixtures / graders    # 评测资产（按需）
```

`skills` CLI 会递归发现仓库中的 `SKILL.md`，因此每个一级目录都可以作为独立技能安装。

## 使用前先看依赖

每个 Skill 的依赖不同。调用前请阅读对应 `SKILL.md`：

- Figma 等外部工具流程需要对应应用、权限或授权状态。
- 图片高清化需要 Gemini API Key，并可能产生 API 费用。
- 网页检索、GitHub 源码验证和远程发布需要网络访问。
- 标注为 optional 的 Skill 缺失时应降级执行，而不是伪造能力。

## 开发与验证

修改 Skill 后，至少检查 frontmatter 与目录结构：

```bash
python /path/to/skill-creator/scripts/quick_validate.py ./<skill-name>
```

如果 Skill 自带脚本、测试或 grader，还应运行对应验证。不要把成功加载 `SKILL.md` 当作工作流已经通过验证。

## 更新

通过 `skills` CLI 安装后，可以更新全部或指定 Skill：

```bash
npx skills@latest update
npx skills@latest update aw-find-and-port-ui-component
```

更多安装选项参见 [`skills` CLI](https://github.com/vercel-labs/skills)。
