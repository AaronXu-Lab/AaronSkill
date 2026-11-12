# 平台产物与验证契约

- Web：favicon.svg 优先使用对应场景 adaptive；favicon.ico 为固定 light 回退。Touch 180px 使用满幅不透明 light 方图，无预烘焙圆角。PWA 192/512 ordinary 及 512 maskable，manifest 只引用相对图标路径，集成时合并 icons，不覆盖产品字段。
- Apple：`.icon` 与传统 `.icns` 并存。Default/Dark 分别使用真实 light/dark 背景及前景；Tinted 使用透明底不透明白色 Mono。用项目 compose-app-icon 的 validate_icon.py 和 icon-schema.json 实际校验（遵循依赖的 uv 预检）。Icon Composer 可用时以 ictool 真渲染 iOS/macOS 的 Default、Dark、TintedLight/Dark、ClearLight/Dark。不可用时仅允许报告跳过引擎，不能称已验证。渲染图放临时目录。
- ICNS：16/32/128/256/512 点各 1×/2×，最大 1024px，固定 light；同一构图。iconutil 打包后将 16/32px 转成传统 RGB RLE 与独立 Alpha 块规避 ARGB 漂移，再解包核对十张 PNG 的尺寸与 RGBA 字节。缺图、像素不符均失败，不交付临时 iconset。
- 菜单栏：透明底单色 Template SVG 与 16px/32px 1×/2× PNG；Windows 托盘为浅/深背景各自单色 ICO，不缩小全彩 app 图冒充状态图。
- Windows：app.ico 的 16/24/32/48/64/128/256 同一场景构图，托盘另行评估。ICO 不能内部切换主题。
- Linux：app.svg 取本轮显式基础源，按配置导出轮廓，支持时保留主题行为。不能把它作为下一轮生成器的源依赖。
- Android：一套 adaptive resources 和 monochrome，全部密度安全区一致，不复制明暗树。重要可见前景须处于画布直径 2/3 安全圆；PWA maskable 是直径 80% 安全圆。用 Alpha >0 的实际可见前景像素测量可见边界并等比缩放并逐像素复查（包括抗锯齿边缘），不能仅验证缩过的画布。Play Store 512px 为满幅不透明直角 32-bit RGBA PNG，Alpha 通道存在且全 255。

所有 PNG 核对尺寸/Alpha；base 固定与 adaptive 的两种主题用真实 SVG 渲染比较像素。先在临时目录完成生成及全部必要检查，再替换受管文件。引擎渲染检查不等于产品集成；不修改 HTML、Xcode、Gradle 或打包配置。
