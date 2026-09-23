# Avatar

Gallery ID: `avatar`

## Definition & Semantics

Avatar 表示人员或承担参与者身份的主体，帮助用户识别作者、所有者或协作者。Avatar 本身是身份图像，不代表在线状态、选择状态或账户操作。

## When to Use

需要建立人员身份与内容或入口的对应，且界面同时提供姓名或其他可识别身份信息时使用。单个账户入口也可以使用 Avatar。未提供头像时，中性默认图只表示图像缺省，不代表匿名权限或账户异常。

## When Not to Use

不要用人物头像表示文件格式或一般资源类别。不要仅靠头像轮廓说明“当前已选择”或“正在运行”，这些判断需要独立的选择或状态表达。

## Similar & Easily Misused Components

- [Symbol](symbol.md) 同样辅助识别对象，但主要承载类别图标或对象图像；人员身份优先使用 Avatar，资源类别优先使用 Symbol。选择依据是主体语义，不是圆形还是方形。
- [Badge](badge.md) 表示身份的属性或状态，不能替代身份本身。

## Composition

### Recommended

在 [Menu Item](menu-item.md) 的人员入口或协作者列表中，将 Avatar 与同一人的姓名关联；角色或状态另由 Badge 表达。账户菜单需要独立触发器，Avatar 只作为该触发器的身份内容。

### Avoid

不要给整行人员入口与其 Avatar 分配互相冲突的目的地而不说明差异。不要把嵌在可操作条目中的头像再做成相同操作的第二个独立控制。

## Internal Usage

图像与身份名称必须指向同一主体。当前组件在缺少 `src` 时提供中性图，但不负责图片加载失败后的自动替换；不能把默认图当作身份核验结果。

## Examples

### Recommended

协作者列表用 Avatar 辅助识别姓名，旁边单独显示“所有者”。

### Problematic

连接器列表用随机人物头像表示连接器类别，用户无法判断该图像代表资源还是负责人。
