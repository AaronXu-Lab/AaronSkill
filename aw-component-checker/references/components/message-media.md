# Message Media

Gallery ID: `message-media` · 家族：Message

## Definition & Semantics

Message Media 是会话内图片或视频的预览入口，帮助用户从消息中辨认媒体并进入完整查看。视频的缩略预览与打开完整媒体属于同一资源的不同查看阶段。

## When to Use

图片或视频本身有助于理解消息，缩略内容比单独文件名更能支持辨认时使用。媒体应与所属消息及其说明一致。

## When Not to Use

不要用 Message Media 表示音频、普通文档或文件上传过程。图片只是用于标识用户或对象时，应采用相应身份组件，而不是给装饰图片添加完整预览流程。

## Similar & Easily Misused Components

- [Lightbox](lightbox.md) 提供完整预览，Message Media 提供消息内入口并已内置对应 Lightbox。
- [File Chip](file-chip.md) 优先表达文件身份；Message Media 优先表达可见媒体内容。
- [Composer Attachment](composer-attachment.md) 管理草稿材料和上传状态；Message Media 展示消息中的媒体。

## Composition

### Recommended

作为 [Message Query](message-query.md) 或 [Message Answer](message-answer.md) 的媒体内容，并让相邻说明指向当前媒体。下载地址可以与预览地址不同，但必须属于同一资源。

### Avoid

不要再在整张 Message Media 外包一层点击打开另一个 Lightbox 的触发器，形成一次点击打开两个预览。也不要把同一媒体重复展示成等价缩略图和文件入口，却不给两者不同用途。

## Internal Usage

类型必须正确区分图片与视频，标题识别资源，说明补充语境。失败信息应说明当前媒体不可用，不能伪装成空白图片。预览和下载必须维持相同文件身份；视频的预览播放不表示任务正在执行。

## Examples

### Recommended

助手提供一个演示视频，消息内显示视频预览，点击进入带播放控件的完整查看。

### Problematic

把 PDF 文件截图当成实际 PDF 预览，下载却指向另一份文件，用户无法确认看到和取得的是否同一对象。
