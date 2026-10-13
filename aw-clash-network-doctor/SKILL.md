---
name: aw-clash-network-doctor
description: "独立处理 Claude 数据清理，或按四块诊断优化 Clash/Mihomo、Android 与应用分流；具体调整获准后执行，记录 IPKK 完整前后结果。"
metadata:
  version: "1.7.0"
  author: "aaron_xu"
  creation_context: "将 Claude 本地数据维护与代理网络、真实环境诊断分别封装为可复用流程，通过明确调整许可、前后测量和恢复验证减少误操作与效果误判。"
---

# Clash Network Doctor

先选择目的：**Claude数据清理**，或**诊断与优化**。清理保持独立，按 [清理分支](references/workspace-cleanup.md) 处理用户指定范围；只扫描时交付清单。

诊断优化读取 [执行工作流](references/workflow.md)，按本次目标选择四块：

1. **网络接管与DNS**：TUN/VPN接管、业务DoH及精确STUN路径。
2. **应用分流与中转**：AI域名、WebKit、Claude.app路径与节点中转。
3. **时区**：系统IANA时区、自动开关及真实浏览器结果。
4. **持久更新与验证**：配置合并、只更新规则、备份安装、完整后测及有限容错。

共同顺序为完整前测→只读诊断列项→沿用或取得具体许可→执行获准块→完整后测及相关验证→交付或恢复。采用实际执行过的措施，记录每项实际验证等级；历史节点和分数按实例读取。

维护updater时读 [事务接口](references/transaction.md)，处理时区时读 [时区核验](references/timezone.md)，复盘效果时读 [执行结果](references/results.md)。

下图展示独立清理分支及四块诊断优化；文本工作流定义授权、验收和停止条件。

![清理与四块诊断优化流程](docs/workflow.svg)
