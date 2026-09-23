# Lightbox

Gallery ID: `lightbox`

## Definition & Semantics

Lightbox 将一个文件的内容放入聚焦的模态预览区域，并可在明确的文件集合内切换。预览、下载和关闭属于同一文件查看任务；组件不是文件管理器，也不自动建立文件集合或获取业务数据。

## When to Use

用户需要从附件、缩略图或文件入口临时查看完整内容，再返回原上下文时使用。图片、视频、文本、代码或文档都可适用，前提是当前文件有明确的预览内容或可解释的加载状态。

## When Not to Use

不要仅为显示一条提示或收集表单输入而打开 Lightbox。需要持续编辑、管理多个对象或对照背景内容完成操作时，预览型模态不是合适的工作区。不应把不支持预览误报为文件不存在或上传失败。

## Similar & Easily Misused Components

- [Sheet Basic](modal-panel.md) 承载临时操作工作区，[Dialog](dialog.md) 围绕确认、说明或输入；Lightbox 的中心任务是查看文件内容。
- [Message Media](message-media.md) 在会话中直接呈现媒体预览，Lightbox 用于进一步聚焦查看。
- [File Chip](file-chip.md) 识别紧凑文件入口，[Composer Attachment](composer-attachment.md) 还表达草稿归属和上传状态；两者可以打开 Lightbox，但不能替代完整内容预览。
- [Code Block](code-block.md) 负责代码阅读与复制，可以作为 Lightbox 的内容，不提供完整文件预览外壳。

## Composition

### Recommended

从 File Chip、Message Media 或已就绪的 Composer Attachment 打开对应文件。由调用方统一提供当前文件身份、内容、下载地址和相邻文件范围；代码内容交给 Code Block，文档内容使用相应查看器。关闭预览后回到原有任务上下文。

### Avoid

内嵌查看器已有局部导航时，不能让同一操作又切换外层文件。不要把需要保存、提交或复杂管理的独立任务塞进 custom 内容，仅因该槽允许任意内容。

## Internal Usage

切换文件时，标题、内容类型、正文、下载目标及加载状态必须一起对应当前文件。加载中、读取失败和不支持预览是不同结果，状态说明应准确区分；预览失败不必禁用仍然有效的文件下载。当前 type 显式选择渲染器，不会因其他内容槽有值就自动切换类型；重试后的业务状态由调用方继续管理。

## Examples

### Recommended

用户从报告附件打开文档预览，在同一附件集合内切换文件；某个预览读取失败时说明失败原因，保留可用下载并提供相应重试入口。

### Problematic

切换到第二个文件后，标题显示新名称，正文和下载按钮仍指向第一个文件，用户无法判断当前查看和保存的对象。
