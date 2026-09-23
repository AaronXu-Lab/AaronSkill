# Composer Attachment

Gallery ID: `composer-attachment` · 家族：Composer

## Definition & Semantics

Composer Attachment 表示当前草稿所附的一份文件，帮助用户确认材料身份、上传状态和是否继续保留。文件预览与从草稿移除是不同操作；移除不自动意味着删除原文件。

## When to Use

文件已加入当前输入，用户在提交前需要确认文件、查看状态或移除材料时使用。文件名、状态和关联 ID 应指向同一份材料。

## When Not to Use

不要用上传卡片表示回答已经生成的产物或普通文件目录条目。预览失败也不等于上传失败，不能因为无法显示内容就把成功上传的文件标成上传失败。

## Similar & Easily Misused Components

- [File Chip](file-chip.md) 是紧凑文件入口；Composer Attachment 额外表达草稿归属与上传阶段。
- [Message Media](message-media.md) 用于会话中的媒体预览，不是待提交附件的管理控件。
- [Lightbox](lightbox.md) 展示文件内容；附件卡片负责文件身份与草稿关系。

## Composition

### Recommended

在 [Composer](composer.md) 附件区域组织卡片。需要成组溢出和相邻文件预览时，可以使用现有 ComposerAttachments 容器统一管理卡片和 Lightbox。

### Avoid

不要把卡片的移除动作与删除文件库原件绑定成同一个未说明的操作。

## Internal Usage

预览入口与移除入口也不应同时触发，或分别指向不同文件。

文件名用于身份识别，类别与大小补充文件属性，状态文案说明上传阶段。单卡片的 state 需要由调用方正确映射；卡片不会根据 file.status 自动推导显示。加载或上传失败时不提供正常预览入口；上传成功后的预览加载、失败与重试归 Lightbox 内容状态。

## Examples

### Recommended

用户在发送前查看附件名称并移除误选文件；另一份已上传文件的预览失败，仅在 Lightbox 中提供重试。

### Problematic

点击附件上的移除按钮后，文件库原件也被删除，界面却只说明“从当前消息移除”。
