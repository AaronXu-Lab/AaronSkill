---
name: aw-design-fake
description: "Integrate or review placeholder interactions, shared fake data, source-code displays, and demo states that can be turned off in frontend prototypes, and maintain a shared fake bundle. Not for unit-test mocks, network mocks, or production feature implementation."
metadata:
  version: "1.8.1"
  author: "aaron_xu"
  creation_context: "原型与设计验证工程里的占位交互、占位文案和演示数据长期靠人凭记忆各写各的，导致同一语义的假数据出现多份副本、假提示混进真实链路、演示开关关不干净。为把 fake 的分层判断、统一入口和真实契约隔离固化成与具体项目无关、可同步可校验的流程而创建。"
---

# AW Design Fake

让原型里的占位操作、内容和演示状态使用统一、可移除的入口，并与真实业务隔离。已接入的真实契约数据、状态和交互始终优先；全局假数据开关不得覆盖真实内容或真实空态、加载态、错误态、未绑定及凭证失效状态。假数据只补充明确未接入区域，或通过显式、可退出的独立演示场景展示。全局资产由 Skill 维护，项目通过共享 bundle 与自有 adapter 接入。

## 选择本次任务

先根据完整会话确认审查或修改模式与原型边界；已有目录和授权直接沿用。按 [文本工作流](references/workflow.md) 的相关章节执行，参考资料只在下列场景读取：

| 需求 | 入口与必要资料 |
| --- | --- |
| A：未实现控件需要点击、选择或提交反馈 | [占位操作](references/workflow.md#占位操作)：调用 `showFakeSonner()`，保留需要的瞬时 UI 状态。 |
| B：假文案、数值、时间、媒体或条目 | [占位内容](references/content.md)：先查 `FAKE_DATA`，再组合业务域 fixture。 |
| 代码展示、高亮、软换行或复制 | [源码消费](references/code-demo.md)：唯一 canonical 文本逐字复用，展示不执行。无 bundle 且已有 fixture 时直接接入该入口。 |
| C：完整演示对象、列表详情联动、流程推进 | [演示状态](references/simulation.md)：统一 selector，开关关闭后所有读取入口一致关闭。 |
| 初始化、同步、异常 bundle 状态 | [接入与同步](references/bundle.md)：先 `--check`，再处理对应状态；保留 adapter、扩展和较新版本。 |
| 全局字段不足，或维护本 Skill | [维护约定](references/maintenance.md)：核对全局写入授权、canonical 资产、版本与适用检查。 |

“fake action”不是任意模拟逻辑的通称，选择满足需求的最小层级。单元测试 mock、网络 mock 和正式生产功能不采用本 Skill。

## 共同边界与完成条件

- 已接入真实契约的 UI 始终读取和呈现真实数据与状态；全局填充开关只控制未接入区域的补充 fixture，不得将真实空态、加载态、错误态或业务状态回退成演示成功态。
- 真实与演示的数据来源、状态和写入路径隔离；fake ID 不进入真实写接口，模拟只写本地演示状态，不改变真实 API、权限、DTO 或 service 契约；源码只作为文本展示。
- 模拟场景通过显式、可退出的入口进入并返回真实场景；查看真实契约不依赖关闭全局假数据开关。
- 不给用户可见内容添加「演示 / Fake / Mock」等来源标签；真假边界由代码结构、身份与请求隔离维护。
- 项目接入不自动授权修改安装 Skill。仅审查不写入；已授权的本地实现、适用检查与失败修复连续完成，不在第一版后默认暂停。
- 按 [验证与交付](references/workflow.md#验证与交付) 检查本次分支，交付可移除实现或审查报告，说明入口、版本、通过项与具体缺口。同步状态 `current` 不等于 adapter 已接好或交互已验证。

![AW Design Fake 工作流程](docs/workflow.svg)
