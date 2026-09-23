# File Chip

Gallery ID: `file-chip`

## Definition & Semantics

File Chip 以文件名代表一个具体文件，可以提供主要文件操作和独立下载入口。文件身份、打开行为与下载行为应始终指向同一个文件。

## When to Use

文件作为消息附件、结果产物或引用出现，名称足以支持识别且不需要完整文件管理行时使用。没有可执行主操作时，应明确采用静态形式。

## When Not to Use

不要用 File Chip 表示任意标签、一般资源导航或上传进度。需要选择、权限、修改时间等多属性管理时，使用对应列表或表格结构。

## Similar & Easily Misused Components

- [Composer Attachment](composer-attachment.md) 表示尚在编写范围中的附件，并区分上传状态与移除；File Chip 表示紧凑文件入口，不拥有上传生命周期。
- [Message Media](message-media.md) 在消息中直接呈现媒体预览；File Chip 以文件名识别内容。
- [Badge](badge.md) 表示属性或分类，File Chip 表示可被访问的具体文件。

## Composition

### Recommended

在 [Message Query](message-query.md) 或 [Message Answer](message-answer.md) 的附件范围中使用 File Chip。主操作需要预览时，由调用方控制 [Lightbox](lightbox.md)；下载入口独立执行该文件的下载。

### Avoid

不要把可操作 File Chip 嵌入另一枚承担相同点击的按钮。主区域与下载入口可以并存，但不能让下载同时触发预览，或让两个入口操作不同版本的文件而没有说明。

## Internal Usage

文件名应保留可识别的文件身份，图标应匹配文件类别。当前组件默认可点击，但不会因存在文件名就自行获得打开能力；没有处理行为时设置为静态。下载入口只应在调用方实际提供下载行为时展示。

## Examples

### Recommended

结果消息附带报告文件，点击名称打开预览，点击独立下载入口保存同一份报告。

### Problematic

上传中的文件直接展示可点击 File Chip，用户无法判断文件是否就绪，点击也没有实际结果。
