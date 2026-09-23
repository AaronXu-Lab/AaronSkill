# Pagination

Gallery ID: `pagination`

## Definition & Semantics

Pagination 在同一有限内容集合的相邻数据页之间导航，保持集合身份不变。当前组件提供上一页、下一页和可选范围文本，不包含数字跳页、每页条数选择或数据获取。

## When to Use

当集合已明确分成多页，用户需要查看相邻范围，且调用方知道当前页、页数和总量时使用。分页应控制同一个经过筛选与排序的结果集。

## When Not to Use

不要用 Pagination 表达流程步骤、对象详情之间的跳转或视图模式切换。只有一页或无结果时不需要分页，当前组件也会隐藏；未知总页数的数据流不能用编造总数适配。

## Similar & Easily Misused Components

[Tabs](tabs.md) 切换同级内容类型，Pagination 切换同一集合的范围。[Turn Navigator](turn-navigator.md) 跳到长会话中的已有轮次，不对集合分段。[Table](table.md) 是被分页内容的一种载体，本身不负责换页。

## Composition

### Recommended

靠近 Table 或 [Grid Item](grid-item.md) 集合放置，由调用方统一管理页码、范围、数据和翻页事件。筛选条件改变后，页码及总数必须与新结果相符。

### Avoid

不要让两个分页器控制同一集合却各自保存页码。不要同时让无限追加和翻页悄然改变同一内容范围，而不向用户说明边界。

## Internal Usage

范围文字应描述实际显示的记录范围，总数对应当前集合。上一页和下一页指向相邻数据页；调用方应正确处理边界。simple 只省略范围展示，并没有取消当前 API 对总量和页数的要求。

## Examples

### Recommended

59 条结果每页展示 20 条，第二页范围为 21–40，前后按钮加载同一筛选结果的相邻页。

### Problematic

接口不知道总数，却填写 total=999，使界面显示一个看似精确的范围与末页。
