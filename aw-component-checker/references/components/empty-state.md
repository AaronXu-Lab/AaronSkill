# Empty State

Gallery ID: `empty-state`

## Definition & Semantics

Empty State 说明一个已经完成判断的内容区域当前没有对象，并在适当时提供形成内容的下一步。空缺是已知结果，不是加载过程或未知结果。

## When to Use

已确认集合为空、筛选无匹配结果或局部关联为空时使用。整块内容需要原因或行动时采用 block；局部空缺只需一句说明时采用 inline。

## When Not to Use

不要在请求尚未完成时提前显示“暂无内容”，也不要将失败或权限不明归为空集合。对象仍存在但部分属性为空时，应在相应字段表达缺值，而非替换整个内容区。

## Similar & Easily Misused Components

- [Skeleton](skeleton.md) 与 [Spinner](spinner.md) 表示结果尚未就绪，Empty State 表示结果已确认。
- [Alert](alert.md) 解释失败或限制。失败导致无法读取集合时，不能只给出 Empty State。
- [Detail Field](detail-field.md) 表达单一属性缺值；Empty State 表达一组对象或独立内容区域为空。

## Composition

### Recommended

将 Empty State 放在原集合的内容区域内，保留相关标题与 [Filter Bar](filter-bar.md)。筛选导致无结果时，下一步指向调整条件；需要新建对象时，使用明确的 [Button](button.md)。

### Avoid

不要在同一内容区域同时显示有效列表与代表整个集合为空的提示。局部空缺需要添加对象时，可以保留所在 Section 的既有操作入口；需要独立原因和行动结构时选择 block。

## Internal Usage

标题说明什么为空，说明解释原因或形成内容的方式，操作与该原因一致。inline 只渲染图标与标题，不承载说明和操作。不要让“无搜索结果”的标题配上无关的新建行动，也不要在无权限时承诺用户可以创建对象。

## Examples

### Recommended

已加载的结果集合没有匹配项，内容区说明“没有匹配结果”，并允许清除当前筛选。

### Problematic

服务器尚未响应就显示“还没有文件，立即上传”，响应到达后该提示又被已有文件替换。
