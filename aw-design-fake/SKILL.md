---
name: aw-design-fake
description: "为前端原型接入或审查占位交互、统一假数据、源码展示与可关闭的演示状态，维护共享 fake bundle。不用于单元测试 mock、网络 mock 或生产功能实现。"
metadata:
  version: "1.6.1"
  author: "aaron_xu"
  creation_context: "原型与设计验证工程里的占位交互、占位文案和演示数据长期靠人凭记忆各写各的，导致同一语义的假数据出现多份副本、假提示混进真实链路、演示开关关不干净。为把 fake 的分层判断、统一入口和真实契约隔离固化成与具体项目无关、可同步可校验的流程而创建。"
---

# AW Design Fake

让原型里的占位操作、内容和演示状态使用统一、可移除的入口，并与真实业务隔离。全局资产由 Skill 维护，项目通过共享 bundle 与自有 adapter 接入。

## 选择本次任务

先根据完整会话确认审查或修改模式与原型边界；已有目录和授权直接沿用。按 [文本工作流](docs/workflow.md) 的相关章节执行，参考资料只在下列场景读取：

| 需求 | 入口与必要资料 |
| --- | --- |
| A：未实现控件需要点击、选择或提交反馈 | [占位操作](docs/workflow.md#占位操作)：调用 `showFakeSonner()`，保留需要的瞬时 UI 状态。 |
| B：假文案、数值、时间、媒体或条目 | [占位内容](references/content.md)：先查 `FAKE_DATA`，再组合业务域 fixture。 |
| 代码展示、高亮、软换行或复制 | [源码消费](references/code-demo.md)：唯一 canonical 文本逐字复用，展示不执行。无 bundle 且已有 fixture 时直接接入该入口。 |
| C：完整演示对象、列表详情联动、流程推进 | [演示状态](references/simulation.md)：统一 selector，开关关闭后所有读取入口一致关闭。 |
| 初始化、同步、异常 bundle 状态 | [接入与同步](references/bundle.md)：先 `--check`，再处理对应状态；保留 adapter、扩展和较新版本。 |
| 全局字段不足，或维护本 Skill | [维护约定](references/maintenance.md)：核对全局写入授权、canonical 资产、版本与适用检查。 |

“fake action”不是任意模拟逻辑的通称，选择满足需求的最小层级。单元测试 mock、网络 mock 和正式生产功能不采用本 Skill。

## 共同边界与完成条件

- fake 对象不进入真实写链路，不改变真实 API、权限、DTO 或 service 契约；源码只作为文本展示。
- 不给用户可见内容添加「演示 / Fake / Mock」等来源标签；真假边界由代码结构、身份与请求隔离维护。
- 项目接入不自动授权修改安装 Skill。仅审查不写入；已授权的本地实现、适用检查与失败修复连续完成，不在第一版后默认暂停。
- 按 [验证与交付](docs/workflow.md#验证与交付) 检查本次分支，交付可移除实现或审查报告，说明入口、版本、通过项与具体缺口。同步状态 `current` 不等于 adapter 已接好或交互已验证。

![AW Design Fake 工作流程](docs/workflow.svg)
