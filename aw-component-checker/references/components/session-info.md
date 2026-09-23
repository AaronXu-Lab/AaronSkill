# Session Info

Gallery ID: `session-info` · 家族：Session

## Definition & Semantics

Session Info 是现有会话的补充信息卡，帮助用户在打开会话前辨认来源、创建者、时间及可选状态。组件是展示内容，不自行提供悬浮触发、导航或会话设置。

## When to Use

侧边栏会话名称不足以区分对象，用户需要额外上下文来决定是否打开某个会话时使用。卡片信息应属于当前被预览的会话。

## When Not to Use

不要把 Session Info 当成所有对象通用的信息卡，固定的人物和时间图标不适合任意字段。关键故障处理或必须采取的操作也不应只存在于偶然出现的悬浮信息中。

## Similar & Easily Misused Components

- [Sidebar Item Meta](sidebar-item-meta.md) 在条目内提供紧凑信息；Session Info 补充多项会话详情。
- [Tooltip](tooltip.md) 解释短标签或控件，Session Info 展示一个会话对象的结构化预览。
- [Composer Context Bar](composer-context-bar.md) 选择待提交请求的上下文；Session Info 说明现有会话。

## Composition

### Recommended

与对应 [Sidebar Item](sidebar-item.md) 的调用方预览浮层组合，条目负责打开会话，信息卡负责辅助辨认。可使用 [Badge](badge.md) 补充确实影响会话理解的状态。

### Avoid

不要在信息卡和 Sidebar Item 中维护不同的会话身份或状态。也不要把原本负责展示的卡片扩展为另一套会话操作菜单，混淆查看信息和执行操作。

## Internal Usage

标题识别会话，可选首行表达来源或相关上下文；人物图标对应的内容应为相关人员，时间图标对应的内容应为时间事实。Badge 的状态必须指向该会话，不能把用户身份或项目状态误当成会话状态。

## Examples

### Recommended

悬停一个名称相近的会话时，信息卡补充创建来源、创建者和时间，帮助用户确认要打开的记录。

### Problematic

卡片的人物图标旁显示文件数量，时间图标旁显示订阅价格，结构暗示与内容含义冲突。
