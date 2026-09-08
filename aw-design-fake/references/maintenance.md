# 维护全局资产与 Skill

只有维护资产、生成器、Skill 指令时读取；普通项目接入无需加载本文件。

## 授权与唯一事实源

先检查全局 `FAKE_DATA` 是否已有所需语义，不能在业务 fixture 或生成文件另造同义值。确需新增全局字段时，沿用完整会话中的 Skill 维护授权；已授权则更新 canonical 资产并同步。若当前只授权项目修改，指出缺失字段与拟修改资产，在必要的全局写入前取得授权；可独立完成的已授权项目工作继续。

项目专有的条目组合保留在业务域 `fake.ts`，不回灌为全局资产。生成的 `data.ts` 不是手写事实源，不通过修改副本或只改项目版本伪装完成。

## 数据资产


`data.ts` 不是手写文件，它由以下 canonical 资产生成：

| 资产 | 内容 |
| --- | --- |
| [references/fake-data.csv](fake-data.csv) | 字段表：`key,kind,value,note`。`key` 用点号表达嵌套，`kind` 取 `string` / `number` / `boolean` / `list` / `asset` / `longform` / `source`，`list` 用 `\|` 分隔。`string` 保留 value 的原始空白，含逗号或换行时按 CSV 规则加引号。 |
| [references/fake-longform.md](fake-longform.md) | 长文正文。二级标题即字段名，段落用空行分隔；多段落生成数组并以 `<br/>` 连接。 |
| [assets/code/conway.ts.txt](../assets/code/conway.ts.txt) | 唯一 canonical 演示源码：完整 TypeScript 生命游戏文本。CSV 的 `code.source,source,code/conway.ts.txt` 指向它，UTF-8 逐字读取，不执行。 |

`asset` 字段调用 `assetUrl`，由项目 `adapter.ts` 决定真实 URL；`source` 是 `assets/` 内的文本路径（拒绝越界路径及指向界外的符号链接），直接序列化为字符串，不走长文段落处理。CSV 必须使用四列表头；key 不得重复或有层级冲突，number 必须有限，boolean 仅接受 true / false。改完数据资产都要提升 `assets/fake/version.ts` 中的 `FAKE_DATA_VERSION`，再同步到项目。消费示例见 [源码消费约定](code-demo.md)。


## 版本

- Skill 版本以 [SKILL.md](../SKILL.md) 的 `metadata.version` 为准。指令、资料、脚本、测试或资源变化按仓库规则更新版本和根 README；默认 MINOR，小修 PATCH，未获明确授权不提升 MAJOR。保留 author 与 creation_context，不添加供应商专属 metadata。
- 数据与 action 版本以 [assets/fake/version.ts](../assets/fake/version.ts) 为准。兼容新增数据字段提升 `FAKE_DATA_VERSION` 的 MINOR，小修 PATCH；只有通用 action 行为改变才提升 `FAKE_LOGIC_VERSION`。字段删除、重命名或不兼容行为涉及 MAJOR，必须先核对明确授权。
- 流程变化先更新 `docs/workflow.md`，再同步 SVG 与入口。数据、action、Skill 三种版本按各自实际变更决定，不机械联动。

## 验证

在 Skill 根目录运行适用于本次变更的检查，实验输出放仓库外临时目录：

| 变更 | 检查 |
| --- | --- |
| 每次 Skill 更新 | 基础 `skill-creator/scripts/quick_validate.py` 与 `aw-meta-skill/scripts/validate_aw_skill.py` 两项校验，核对元数据、链接、README 版本。路径按环境解析。 |
| 描述、路由、授权或完成条件 | 用适用请求、容易误触发的反例、局部修改请求走查；实质调整时做隔离项目回放。记录读取范围、完成结果、额外确认与越界行为，不以字数下降当作效果提升。 |
| canonical 数据、源码、action 或生成器 | `node scripts/fake-bundle.mjs --self-check`；检查值、源码指纹、生成文本与同步。修改源码基线须有用户明确更换源码的依据。 |
| 跨层接入、adapter 或状态行为 | 运行受影响的原型集成/项目检查；有新流程或非平凡交互时按项目约定验证浏览器。 |
| 工作流或 SVG | 检查文本与图语义一致，图或流程改变时渲染目视复核。 |

纯描述或文档小修不自动跑 bundle 全量回归；已通过且未受新改动影响的检查无需重复。修复本次变更引起的问题，重验受影响项，保留原始证据到临时目录。
