# Mac updater事务接口

用于维护本次已实现的`.command`。执行与容错条件统一采用 [工作流第四块](workflow.md#4-持久更新与验证)，本文保存已使用的接口和保护项。

## 输入、持久合并与保护

活动文件为`~/.config/clash.meta/XSUS.yaml`、`ADJUST_RULE`及`UPDATE_SUBSCRIPTIONS_AND_ADJUST_RULES.command`。执行前定位本机实际文件、客户端helper和API，按当前架构运行隔离核心校验。

已使用互斥锁、私有候选目录、独立备份及原子替换。合并器实际用于DNS、指定节点dialer-proxy、prepend规则和Fake-IP排除。逻辑规则按括号深度解析，兼容核心API的规范化表示；Fake-IP排除与prepend规则分段合并，AXO规则及排除按本机原合同保留。

DNS验证使用RFC8484应答；隔离核心TUN关闭并绑定物理接口，使用独立目录/端口，复用本机geodata。核心节点预查与实际正常路径验收分别记录。

## 已实现的命令模式

| 参数/模式 | 实际行为 |
| --- | --- |
| 默认下载 | macOS系统curl按客户端User-Agent下载，证书校验开启，URL由stdin输入；真实下载检查通过 |
| `--check` | 合并、核心和隔离DNS/节点检查，记录诊断；活动YAML和订阅时间保持 |
| `--source FILE` | 本地订阅输入，跳过下载及更新时间写入；已用于同步安装 |
| `--rules-file FILE` | 校验后安装持久规则，异常恢复原overlay |
| `--rules-only` | 已安装XSUS作输入，仅允许rules变化，校验期间活动文件改变则停止；默认保留网络状态 |
| `--preserve-network-state` | 沿用全部Selector选择；主动缓存维护/关闭连接参数与其互斥，冲突在修改前返回参数错误 |
| `--await-safari` | 本地监测进程等待真实Safari的开始/最终决定，有限等待和超时恢复 |

仅规则模式的字段保护通过实际函数检查：规则增量可接受，DNS/节点/组/profile/IPv6变化或缺失非rules键均拒绝。重复合并幂等、策略组覆盖保持、互斥参数和保留网络状态默认行为均有验证记录。

下载分支曾出现Python证书信任库错误；改用系统curl后，实测下载、合并和隔离检查通过。源配置与订阅更新时间的实际变化分别核对。

## Safari双阶段事务

实际记录包含transactionId、stage、pid、configSha256（兼容config_sha256）、backupPath、decision、updatedAt及healthPolicy。

1. 安装后`await-safari-start`接受当前事务的`start`，启动持续观察。
2. 观察完成进入`await-safari`，完整Safari结果及业务恢复满足条件后写`pass`，失败写`fail`。
3. 写入前重读并核对ID、stage、存活PID与活动配置SHA；保留原字段，仅更新决定及时间。临时文件0600，fsync/os.replace原子写入。
4. 开始和最终等待各有300秒上限；本地进程负责超时回滚。
5. 保存最终committed/rolled-back记录，等待进程退出，再清理当前事务标记与自建资源。

healthPolicy保存观察时长、连续失败阈值、累计比例/最小轮次、最终成功轮数、恢复窗口、请求重试次数及网络状态模式。阈值的事实源是 [有限容错验收](workflow.md#有限容错验收)。

## 留证与恢复

每轮保留时间、目标、路径、退出码、HTTP、DNS/TCP/TLS/总耗时；CONNECT仅为对照。保存累计失败、最长连续失败和最终连续成功；恢复不删除首次失败。

备份覆盖YAML、overlay、updater及运行/相关偏好。实际曾由脚本恢复YAML/overlay，再从独立初始备份恢复updater；最终核对三个文件哈希、全部Selector及正常联网。观察失败、文件恢复和联网恢复分别记述。完整配置及节点凭据保持私有。
