---
name: aw-clash-network-doctor
description: "独立清理 Claude 数据；持续优化 macOS 目标网站分数，选择 Clash 配置并持久化更新；Android 沿用四块诊断。"
metadata:
  version: "1.12.0"
  author: "aaron_xu"
  creation_context: "将 Claude 本地数据维护与代理网络、真实环境诊断分别封装为可复用流程，通过明确调整许可、前后测量和恢复验证减少误操作与效果误判。"
---

# Clash Network Doctor

先选择目的：**Claude数据清理**，或**诊断与优化**。清理保持独立，按 [清理分支](references/workspace-cleanup.md) 处理用户指定范围；只扫描时交付清单。

诊断优化读取 [执行工作流](references/workflow.md)：

- **macOS**：以 IPKK、Net.Coffee、CLIS 三站真实分数尽可能提升为目的，各站独立前后对照。多份可更新配置且未明确目标时先询问；区分一次性修正与更新后重放，按需适配 `.command`。诊断、修改及订阅更新后核对活动配置与 overlay/入口绑定、域名及应用进程/路径规则、节点、核心加载和目标应用新连接命中；已授权目标的缺失应用规则须补入持久 overlay 与对应更新入口并验收，纯只读诊断只报告。STUN、DNS、网页与业务出口分别留证。对照测试、保留最佳有效状态，直到达到可确认满分或当前范围内无有依据的可行提升路径，并报告限制。
- **Android**：保持既有四块诊断、获准调整与完整前后验收流程。

按本次目标选择四块措施：

1. **网络接管与DNS**：TUN/VPN接管、业务DoH及精确STUN路径。
2. **应用分流与中转**：AI域名、WebKit、Claude.app路径与节点中转。
3. **时区**：系统IANA时区、自动开关及真实浏览器结果。
4. **持久更新与验证**：配置合并、只更新规则、备份安装、完整后测及有限容错。

共同顺序为完整前测→只读诊断列项→沿用或取得具体许可→执行获准块→完整后测及相关验证→交付或恢复。macOS 按工作流循环继续优化；措施以当次证据选择，记录每项实际验证等级，历史节点和分数仅作实例。

维护updater时读 [事务接口](references/transaction.md)，处理时区时读 [时区核验](references/timezone.md)，复盘效果时读 [执行结果](references/results.md)。macOS 优化前读 [三站评分与证据边界](references/diagnostic-tools.md)，记录三站基线、候选复测及最终结果，不合成总分。

下图展示独立清理、macOS 持续优化与 Android 四块诊断；文本工作流定义授权、验收和停止条件。

![清理与分设备网络优化流程](docs/workflow.svg)
