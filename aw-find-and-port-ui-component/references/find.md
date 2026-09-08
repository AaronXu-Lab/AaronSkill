# Find：发现并比较组件

仅在工作流选定 Find 后读取。共同证据、授权和停止边界见 [工作流](../docs/workflow.md)。以下命令以 Skill 根目录为工作目录。

## 刷新与搜索

每轮 Find 开始刷新一次目录，同轮原词、别名和候选细化查询复用该次结果：

```bash
python3 scripts/refresh_catalogs.py --json
```

仅在用户要求最新结果、来源已发生变化或出现需要重新获取的证据时再次刷新；不要因更换搜索词重复刷新。刷新失败时保留旧缓存并标记 `stale`；无可用缓存标记 `unavailable`，不能写成无匹配。目录被截断或来源配置变化时，不把不完整或旧解析结果当作新的完整目录。

目录中的 `port_eligible: false`、`verification_status: unverified` 和 `requires_verification: true` 表示待核验，不代表已判定不兼容。刷新时间只证明目录获取，不能充当源码核验时间。搜索 `match` 是词面排序提示，不是最终行为判断。

请求描述行为或使用别名时读取 [组件别名](component-aliases.md)，按原词及有用别名搜索：

```bash
python3 scripts/search_catalogs.py --query "<component>" --alias "<alternate term>" --json
```

## 核验与比较

对有希望的候选执行 [来源核验](source-retrieval.md)，检查预览与源码的一致性、维护状态以及目标兼容性。没有目标项目信息时明确兼容性假设，不编造已安装依赖。

内置目录当前提供 Base UI 或原生变体线索，包括 shadcn/ui Base、coss ui、Dice UI Base、ReUI 公开 MIT 仓库、exaBase Design System V4 和 Fluid Functionalism。这是发现范围，不是永久兼容性结论，也不限制 Port 的准确来源。

- 目录缺少合适候选时，检查同一库当前官方变体；准确变体不兼容不能推导整个库不兼容。
- ReUI：仅接受可追溯到公开仓库的源码，付费或鉴权分发单独处理。
- exaBase：准确区分上游与 ExaWizards 来源；复制部分涉及 CC BY 4.0 时保留所需署名与修改说明。
- Fluid Functionalism：同时存在 Base UI 与 Radix 变体时优先检查 Base UI registry 项；沿准确项的依赖图核验，名称不能证明基础依赖。
- 按行为将候选分为 `Exact`、`Equivalent`、`Composite`，依次优先；不能把词面命中当成满足需求。

只有用户明确要求时才扩展内置来源之外的搜索，并核验新增来源的官方文档、准确实现、许可证、维护状态与兼容性。将其加入 `references/sources.json` 持续维护前另需用户批准。

## 交付

交代所有配置来源与刷新状态。用比较表记录库、组件、行为匹配、预览、准确源码、许可证／来源、基础依赖证据、兼容性与核验时间。准确变体不兼容的结果单独列出证据与原因；明确标注 stale、unavailable 和待验证项。

以推荐候选（或无）、关键理由、取舍及“请明确选择候选后再进入 Port”结束。遵守工作流的 Find 停止点。
