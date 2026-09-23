# Turn Navigator

Gallery ID: `turn-navigator` · 家族：Conversation Navigation

## Definition & Semantics

Turn Navigator 是当前会话内的轮次导航，将一组请求摘要映射到可跳转的消息位置。当前项表示阅读位置，不表示消息被选择用于批量操作，也不改变会话内容。

## When to Use

会话较长，用户确实需要在不同请求之间回看，并且界面能够容纳独立导航区域时使用。每个导航项必须对应可定位的轮次，调用方负责跳转和当前项同步。

## When Not to Use

短会话没有实际跳转需求时不必增加导航。不要用 Turn Navigator 在不同会话间切换，也不要把每个流式片段都当成独立轮次。

## Similar & Easily Misused Components

- [Pagination](pagination.md) 更换集合中显示的一页数据；Turn Navigator 在同一会话内容中定位，不分页加载或替换内容。
- [Tabs](tabs.md) 切换同层内容区域；Turn Navigator 的目标仍属于同一条连续会话。
- [Sidebar Item](sidebar-item.md) 可以导航到另一个会话，Turn Navigator 只导航当前会话内部。

## Composition

### Recommended

与会话消息区域并置，使用 [Message Query](message-query.md) 的轮次身份或调用方维护的定位映射连接目标。滚动阅读时同步当前项，使导航反映实际位置。

### Avoid

不要让另一套分页或标签切换也使用同一组轮次编号，却改变内容集合。也不要复制一套仅在点击后更新、与滚动位置无关的“当前轮次”状态。

## Internal Usage

每个摘要应能帮助辨认对应请求，标识应稳定且唯一。预览文字与实际目标必须一致；导航项数量和显示条件由调用方决定，组件本身不会判断会话是否足够长，也不会自动滚动页面。

## Examples

### Recommended

用户在较长会话中预览某条请求摘要，点击后回到该请求，继续滚动时导航更新当前轮次。

### Problematic

导航摘要写“导出报告”，点击却打开另一个会话；组件宣称的内部定位被替换为跨会话导航。
