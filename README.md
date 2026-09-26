<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="AaronSkill：一组可直接安装的实用 Agent Skills">
</p>

<p align="center">
  <strong>把真实工作流封装成可发现、可验证、可复用的 Agent Skills。</strong>
</p>

<p align="center">
  设计系统 · UI/UX · 品牌资产 · Figma 工具 · Skill 工程 · 内容工作流
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

目前共收录 **19 个 Skill**，按主要用途分为元 Skill、工具类、资源获取、设计支撑和设计 Agent；另设 Working On 分组，并单独标记不再维护的 Skill。

### 元 Skill

用于创建、升级和规范化其他 Skill 的元能力。

| Skill | 版本 | 它解决什么问题 | 关键边界 |
| --- | --- | --- | --- |
| [`aw-meta-skill`](./aw-meta-skill/) | `1.9.1` | 创建或更新任何 Skill，完整替代 `skill-creator` 作为统一入口 | 按变更范围读取与验证；Markdown 为执行事实源，SVG 细则按需加载 |

### 工具类

面向明确输入与结果的实用工作流，帮助完成资产加工、内容处理或专项工程任务。

| Skill | 版本 | 它解决什么问题 | 关键边界 |
| --- | --- | --- | --- |
| [`aw-logo-asset-cook`](./aw-logo-asset-cook/) | `1.3.1` | 从 SVG 或经评估、迭代重绘的图片生成并验证全平台图标资源 | 用户明确指定输入；低保真转换须确认，重绘通过后仍需兼容性与主题检查 |
| [`aw-mail-read-later`](./aw-mail-read-later/) | `1.1.1` | 从 Outlook 的 `Read Later` 文件夹推荐、阅读、总结或翻译一项内容 | 手动一次处理一项；归档或移除邮件前必须得到用户确认 |
| [`rewrite-like-aaron`](./rewrite-like-aaron/) | `1.1.1` | 将 AI 中文草稿改写为 Aaron 当前的博客文风 | 保留事实与立场；限制口头禅、反问和中英混写的表面模仿 |

### 资源获取

负责从外部来源检索、验证、筛选并整理可用资源。

| Skill | 版本 | 它解决什么问题 | 关键边界 |
| --- | --- | --- | --- |
| [`aw-comic-dossier-packer`](./aw-comic-dossier-packer/) | `1.1.0` | 收集漫画封面、整理来源介绍、生成小红书封面与最终档案 | 高清化需确认费用；社媒图使用原创视觉而非复刻封面 |
| [`aw-logo-finder`](./aw-logo-finder/) | `1.1.0` | 从官网、Logo 资源站和应用商店寻找、比对并导出品牌或产品 Logo | 必须先确认候选与输出尺寸，再生成无损 WebP |

### 设计 · 支撑

为设计系统、组件实现和设计交付提供基础设施、规范与工程支撑。

| Skill | 版本 | 它解决什么问题 | 关键边界 |
| --- | --- | --- | --- |
| [`aw-design-md-author`](./aw-design-md-author/) | `1.7.0` | 按 Google Labs 规范创建、审查和维护完整的 `DESIGN.md` 视觉契约 | 保护所有权与纯注释边界；官方验证不可用时如实报告；不代替代码或 Figma |
| [`aw-design-system-gallery`](./aw-design-system-gallery/) | `3.29.1` | 创建、审查或优化 Gallery 的默认示例、真实设计轴与状态对比 | 组件 Panel 复用当地标准 Default／Properties／Demo 结构；纯健壮性验证不默认进入正式 Gallery；复合展示不替代子级矩阵；Caption 仅含真实公开轴；边界提示接入现有开关并验证两态；项目配置留在目标仓库 |
| [`aw-design-fake`](./aw-design-fake/) | `1.8.1` | 为原型工程统一 fake 数据、演示源码与占位交互，并初始化或同步 bundle | 真实契约数据与状态优先；演示场景显式可退出、写入隔离；源码逐字复用且仅展示不执行；不碰单测 mock |
| [`aw-design-token-consistency-auditor`](./aw-design-token-consistency-auditor/) | `0.9.0` | 比较 Figma Variables、`DESIGN.md` 和 CSS/Less Token | 只生成审计证据，不自动改写 Token |
| [`aw-find-and-port-ui-component`](./aw-find-and-port-ui-component/) | `1.7.0` | 发现、比较并移植具体 UI 组件实现 | 仅处理组件级意图；整应用、页面、工作区或通用文件迁移不触发，Find 与 Port 保持选择门 |

### 设计 · Agent

直接参与界面判断、审查和表达质量控制的设计 Agent。

| Skill | 版本 | 它解决什么问题 | 关键边界 |
| --- | --- | --- | --- |
| [`aw-canvas-design`](./aw-canvas-design/) | `1.5.1` | 用实际组件画布设计多弹层业务流程，`/<业务路由>/design-canvas` 是设计整理入口，支持 `?preview={name}` 单流程走查；附带 canvas-kit 标准件（可直接打开的 HTML 组件与 React 参考实现），通过评论迭代并验收入口覆盖 | 优先复用项目已有画布和依赖，不强制对齐 canvas-kit 版本；画布不是业务正式页面，只有明确要求时才接入实际入口 |
| [`aw-component-checker`](./aw-component-checker/) | `1.24.1` | 审查桌面端组件的语义、组合与内部使用，并维护 Component Reference 和索引 | 按需读取相关规则；纯审查不自动改写；不用于单纯视觉规格检查 |
| [`aw-ux-info-redundancy-audit`](./aw-ux-info-redundancy-audit/) | `1.7.1` | 审计各类 UI/UX 的信息任务价值、语义重复、适用阶段与视觉承载物必要性 | 先输出审计证据与最小改动决策，再实施界面修改 |
| [`aw-wording-reviewer`](./aw-wording-reviewer/) | `0.12.1` | 审查简体中文 UI 的排版、术语、格式、跨组件数据展示与微文案 | 默认只审查不修改；不用于英文、日文或产品信息架构评审 |

### Working On

正在持续完善的 Skill，保留独立目录，可按需安装和使用。

| Skill | 版本 | 它解决什么问题 | 关键边界 |
| --- | --- | --- | --- |
| [`temp-local-service-doctor`](./temp-local-service-doctor/) | `1.1.1` | 启动本地多服务并定位端口、接口与页面加载故障 | 优先复用现有入口；确认进程归属；以调用链和目标页面验证结果 |
| [`temp-prd-verifier`](./temp-prd-verifier/) | `1.1.1` | 从项目 PRD 查证需求并按需与界面或实现对照 | 区分明确规定、推断与未覆盖；只读查证或沿已有授权修正 |
| [`temp-small-improves`](./temp-small-improves/) | `1.1.1` | 显式检查并优化一组容易遗漏的界面排版、控件与动效细节 | 仅用户主动点名时调用；只处理有证据支持的最小改动 |

### 不再维护

以下 Skill 保留在仓库中供已有使用者参考，但不再主动演进或纳入新能力建设。

| Skill | 版本 | 状态 |
| --- | --- | --- |
| [`aw-figma-component-governance`](./aw-figma-component-governance/) | `0.10.0` | 不再维护 |

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
