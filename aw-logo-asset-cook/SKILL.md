---
name: aw-logo-asset-cook
description: 从用户在请求开头明确指定的 SVG 或图标资源目录，解析唯一 SVG 并重建精简且经过验证的全平台图标资源与分平台用法 README；覆盖网页 favicon、Apple Touch、PWA、Apple、Windows、Linux、Android、菜单栏及托盘图标，并处理明暗主题。源图更新或需要刷新这些资源时使用。
metadata:
  author: aaron_xu
  version: "2.4.0"
  creation_context: "为从用户显式选择的 SVG 唯一事实源稳定生成网页 favicon、可引用的安装图标、桌面端、移动端、菜单栏及托盘图标，并提供可随资源同步更新的分平台用法说明；同时在单主题补色、清理产物和 Apple Icon Composer 验证前设置明确授权门禁。"
---

# AW 应用图标资源生成

本 SKILL 独立存放。用户必须在请求开头明确指定源 SVG，或明确指定一个图标资源目录。目录模式只检查该目录根层的 `*.svg`：恰好一个时自动采用；没有时停止并提示；多个时列出候选并询问用户哪个是唯一事实源。不得递归搜索，也不能扫描未被用户指定的当前目录、项目根目录或 SKILL 目录来猜测。

以下两类表达都属于有效的明确指定：直接给出 `/绝对路径/logo.svg`；或像 `/绝对路径/favicon-package` 加“这里有个图标资源”这样，明确把该目录指定为本次图标资源范围。仅提到项目名称、当前目录或“看看图标”而没有给出可解析路径，不算指定。

执行脚本时通过 `--source` 传入该 SVG 或目录的绝对路径；为兼容旧调用，`--source-svg` 是同一参数的别名。

目标 `favicon-package` 默认使用源 SVG 所在目录；目录模式默认使用用户指定的目录。如果用户指定了其他目标目录，以用户指定为准。运行生成时仍必须通过 `--project-root` 显式传入目标目录，禁止根据当前工作目录或 SKILL 所在位置猜测。

## 流程概览

![应用图标资源生成核心流程](docs/workflow.svg)

## 源文件与主题预检

先把用户指定的 SVG 或资源目录唯一解析为可读取的 SVG，再运行只读主题检查：

```bash
python3 scripts/cook.py \
  --source /绝对路径/logo.svg \
  --inspect-theme
```

目录模式可将 `--source` 改为 `/绝对路径/favicon-package`。若根层 SVG 不唯一，脚本只报告候选并停止；由用户选择后，使用所选 SVG 的绝对路径重跑。

主题检查必须发生在依赖安装、清理和资源生成之前。结果分为：

- `dual`：SVG 已包含可区分的 light 与 dark 配色，保留现有几何、颜色及 `prefers-color-scheme` 行为，继续后续流程。
- `single-light`：SVG 只有明色主题，提示用户缺少暗色主题。
- `single-dark`：SVG 只有暗色主题，提示用户缺少明色主题。

单主题的明暗判断依据背景色亮度，只能作为“可能是明色/暗色”的提示；用户明确说明主题归属时以用户判断为准，不得用检测结果覆盖用户语义。

若结果为单主题，必须询问：`检测到该 SVG 只有明色/暗色主题。是否允许 AI 在不改变现有主题和几何结构的前提下补充互补主题色？` 这是阻塞决策；除非用户已经在同一请求中明确授权，否则不得继续。

- 用户拒绝或未授权：立即停止，不安装依赖、不清理现有产物、不修改 SVG，也不生成任何平台资源。
- 用户允许：AI 创建临时的双主题 SVG，不覆盖原始文件，保留原主题全部颜色和几何结构，只为缺失主题推导互补配色。若输入为暗色主题，临时 SVG 必须把 AI 补出的明色设为默认回退，并把原暗色放入 `prefers-color-scheme: dark`；若输入为明色主题，保留其为默认并增加 dark media query。
- AI 补色后分别渲染明暗外观进行视觉检查，再重新运行 `--inspect-theme`。只有结果为 `dual` 才能进入生成；仍为单主题或颜色角色不完整时停止。

AI 补色不是对用户授权的推断。用户只要求生成资源，不代表同意创造新的品牌颜色。

## 依赖预检

运行生成脚本或修改任何生成目录之前，必须检查项目级依赖 `<project-root>/.agents/skills/compose-app-icon`。仅当以下文件全部存在时，才视为安装完整：`SKILL.md`、`scripts/validate_icon.py`、`scripts/icon-schema.json`、`scripts/pyproject.toml`、`scripts/uv.lock`。

若依赖缺失或不完整：

1. 立即停止，不生成资源，也不清理现有产物。
2. 告知用户必须安装 `compose-app-icon`，说明预期安装位置，并请求安装许可。
3. 仅在用户明确同意后，使用 `$skill-installer` 或其他可信的 SKILL 安装方式，将准确的 `compose-app-icon` 安装到 `<project-root>/.agents/skills`。禁止依据模糊名称或未经验证的仓库安装；若找不到可信来源，请用户提供来源，不得猜测。
4. 安装后重新检查必需文件，完整阅读 `compose-app-icon/SKILL.md`，然后自动继续原生成任务。

用户授权前禁止安装依赖。依赖已经存在时，也必须先完整阅读其 `SKILL.md`，并遵循其中的 `uv` 预检要求。

## 生成

运行：

```bash
python3 scripts/cook.py \
  --source /绝对路径/logo.svg \
  --project-root /绝对路径/favicon-package
```

若原 SVG 已是双主题，直接传入原文件；若用户授权 AI 补色，传入已经通过双主题复检的临时 SVG。脚本依赖 `rsvg-convert` 与 Pillow，只会替换各平台的生成目录。脚本自身会再次执行主题门禁，单主题 SVG 无法进入清理阶段。

## 最小产物

- `README.md`：位于目标根目录，使用中文按 Web、iOS/macOS、Windows、Linux、Android 说明各资源的建议用法、主题与遮罩注意事项及产品集成边界。内容使用通用 `app` 语义，不写入具体品牌名。
- `web/favicon.svg`：保留已确认或补齐后的 SVG 主题切换；`web/favicon.ico` 仅作为旧环境的亮色回退。网页 UI 应直接使用该主题感知 SVG。
- `web/apple-touch-icon.png`：180×180 的 iOS/iPadOS 网页主屏幕图标。使用明色主题背景铺满不透明方形画布，不预先烘焙圆角。
- `web/pwa/`：包含普通的 192×192 与 512×512 PNG、不透明全画布且主体位于安全区内的 512×512 maskable PNG，以及使用相对路径引用三张图标的最小 `manifest.webmanifest`。该 manifest 只声明图标；集成时应合并进目标项目现有 manifest，不能覆盖产品名称、启动路径、显示模式和主题色等字段。
- `iOS&macOS/app.icon`：位于 `iOS&macOS` 根目录的唯一 Apple 应用图标产物。Default 和 Dark 必须分别使用最终双主题 SVG 的明暗配色与前景，Tinted 使用专用高对比 Mono 前景。
- `iOS&macOS/menu-bar/`：包含一个 macOS Template Image SVG，以及 1x/2x PNG；由 macOS 自动着色。
- `windows/app.ico`：稳定的应用图标。由于 ICO 无法在内部切换主题，只有托盘保留 `tray-light.ico` 与 `tray-dark.ico`。
- `linux/app.svg`：保留 SVG 内部主题切换。
- `android/`：只包含一套自适应图标资源；系统主题图标使用 monochrome 图层，不重复生成明暗资源树。`play-store-512.png` 是 512×512 的 32-bit RGBA PNG，使用明色主题背景铺满方形画布，保留 Alpha 通道且所有 Alpha 值为 255，不预先烘焙圆角。

生成平台资源时，除根目录用法 README 与最小 PWA 图标 manifest 外，不额外创建产品元数据、清单、预览、校验和、锁文件、联系表；平台原生自适应格式能够处理外观时，也不显式复制明暗资源。

## Apple `.icon` 验证

生成脚本必须使用 `<project-root>/.agents/skills/compose-app-icon` 校验 `app.icon`，再使用 Icon Composer 的 `ictool` 分别渲染 iOS 与 macOS 的 Default、Dark、Tinted（Mono）及 Clear 模式。渲染图仅用于临时验证，不得保留。

当主题由 AI 补齐时，Apple 产物也必须同步使用新主题：`fill-specializations` 同时写入明暗背景，前景分别提供 Default 与 Dark specialization，Mono 仍使用透明底上的不透明白色遮罩。禁止只补 Web SVG 而让 `app.icon` 继续复用单一主题。

若 Icon Composer 本体不可用，保留已经通过 Schema 校验的 `.icon` 包，并明确报告仅跳过了引擎渲染。禁止用 `.icns` 替代所需的 `.icon` 格式。

## 不变量

- 从用户指定或经授权补齐的 SVG 中提取颜色，不在脚本内重复维护调色板。
- 已有双主题 SVG 必须原样保留其几何结构、颜色和 `prefers-color-scheme` 行为。
- 单主题 SVG 未获用户授权时不得修改或生成；获授权时只补缺失主题，不改变原主题的品牌颜色与几何。
- Apple Mono 专用资源必须是透明底上的不透明白色前景遮罩，不能依赖 Icon Composer 从品牌色自动推导 Mono 对比度。
- 应用平台的遮罩由平台负责；不得把圆角烘焙进 iOS、Android 自适应图标或 Icon Composer 背景。
- Apple Touch 与 Play Store 提交图必须是铺满明色主题背景的完全不透明方图，不能保留源 SVG 的透明圆角；系统或商店负责应用最终遮罩。Play Store PNG 还必须显式保留 Alpha 通道，不能因全部像素不透明而优化成 24-bit RGB。
- PWA maskable 图标必须使用明色主题背景铺满不透明画布，并把重要前景限制在平台安全区内；不能把带透明边角的普通应用图标直接标记为 maskable。
- macOS 菜单栏与 Windows 托盘图标必须是透明底单色状态图标，不能直接缩小全彩应用图标。
- 根目录 README 必须与当次实际产物路径一致，分平台说明建议用法与集成边界，不包含具体品牌名，也不能宣称已经修改产品仓库配置。
- 不覆盖产品仓库中的集成代码；本 SKILL 只重建图标资源库。
