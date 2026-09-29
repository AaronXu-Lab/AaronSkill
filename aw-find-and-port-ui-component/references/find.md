# Find：发现并比较组件

仅在请求通过工作流的组件粒度适用门并选定 Find 后读取。查找目标必须是可由角色或行为界定的具体 UI 组件；不要因为应用迁移、页面对齐或本地设计来源中可能包含组件，就启动发现流程。共同证据、授权和停止边界见 [工作流](../references/workflow.md)。以下命令以 Skill 根目录为工作目录。

## 刷新与搜索

每轮 Find 开始刷新一次目录，同轮原词、别名和候选细化查询复用该次结果：

```bash
python3 scripts/refresh_catalogs.py --json
```

仅在用户要求最新结果、来源已发生变化或出现需要重新获取的证据时再次刷新；不要因更换搜索词重复刷新。刷新失败时保留旧缓存并标记 `stale`；无可用缓存标记 `unavailable`，不能写成无匹配。目录被截断或来源配置变化时，不把不完整或旧解析结果当作新的完整目录。

目录中的 `port_eligible: false`、`verification_status: unverified` 和 `requires_verification: true` 表示待核验，不代表已判定不兼容。刷新时间只证明目录获取，不能充当源码核验时间。搜索 `match` 是词面排序提示，不是最终行为判断。

`sources.json` 的 `type` 记录来源默认的交互基础与样式方案；目录条目的 `foundation_hint`、`styling_hint` 仅是线索，不能代替准确组件及传递依赖核验。`foundation`、`styling`、许可证和 Port 资格未经核验时保留 `unverified`，不把目录来源类型写成组件结论。

请求描述行为或使用别名时读取 [组件别名](component-aliases.md)，按原词及有用别名搜索：

```bash
python3 scripts/search_catalogs.py --query "<component>" --alias "<alternate term>" --json
```

## 核验与比较

对有希望的候选执行 [来源核验](source-retrieval.md)，检查预览与源码的一致性、维护状态以及目标兼容性。没有目标项目信息时明确兼容性假设，不编造已安装依赖。

内置目录以 Base UI 来源为主，也收录其他技术基础的组件线索：Base UI 官方仓库、shadcn/ui Base、basecn、coss ui、Dice UI Base、ReUI 公开 MIT 仓库、Fluid Functionalism、Astryx 和 Lobe UI。每轮搜索覆盖所有已配置来源；目录范围不是永久兼容性结论，也不限制 Port 的准确来源。

- 目录缺少合适候选时，检查同一库当前官方变体；准确变体不兼容不能推导整个库不兼容。
- Base UI 官方仓库：提供无样式 React 基础组件；比较和移植时区分它与已封装样式的成套组件实现，并核验目标项目是否已有 `@base-ui/react`。
- ReUI：仅接受可追溯到公开仓库的源码，付费或鉴权分发单独处理。
- basecn：公开 registry 同时包含依赖 Base UI 的组件和原生组件；`drawer` 与 `drawer-base` 是不同条目，`form` 和 `form-tanstack` 的文档路径不同于 registry 名称，按准确 registry 项核验基础依赖与预览。
- Fluid Functionalism：同时存在 Base UI 与其他变体时分别核验准确 registry 项；名称不能证明基础依赖。
- Astryx：官方公开 React／StyleX 源码和 MIT 许可；目录可由公开仓库及文档索引定位候选。移植其源码可能牵涉内部模块、主题与 StyleX，不把预编译 CSS 或单一文件当作独立可移植实现。
- Lobe UI：以 [官方组件文档](https://ui.lobehub.com/) 和已配置的 `llms.txt` 索引定位候选，再到 [公开源码仓库](https://github.com/lobehub/lobe-ui) 核对准确变体。组件可能依赖 Ant Design、Base UI、主题 Provider、动效或内部模块；核验准确源码、依赖、样式和 [仓库许可证](https://github.com/lobehub/lobe-ui/blob/master/LICENSE) 后再推荐。目录里的 `mixed` 和 `antd-style` 只是来源线索，不代表每个组件的基础或转换成本。
- 按行为将候选分为 `Exact`、`Equivalent`、`Composite`，依次优先；这些搜索标签只是词面提示，最终级别按核实的行为确定。行为完全匹配的非 Base UI 候选优先于行为近似的 Base UI 候选；相同匹配程度下优先 Base UI。若两类都有可行候选，都给出推荐并标明来源基础、转换工作量与偏差风险。非 Base UI 来源不预设成品效果较差。

只有用户明确要求时才扩展内置来源之外的搜索，并核验新增来源的官方文档、准确实现、许可证、维护状态与兼容性。将其加入 `references/sources.json` 持续维护前另需用户批准。

## 交付

交代所有配置来源与刷新状态。用比较表记录库、组件、行为匹配、预览、准确源码、许可证／来源、交互基础和样式证据、转为 Base UI ＋ CSS Modules 的工作量与偏差风险、目标兼容性及核验时间。准确变体不兼容的结果单独列出证据与原因；明确标注 stale、unavailable 和待验证项。

以推荐候选（或无）、关键理由、取舍及“请明确选择候选后再进入 Port”结束。遵守工作流的 Find 停止点。
