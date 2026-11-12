## 基础资源选择规则（AI 与人工均适用）

1. 以使用场景为单位：先查已有场景构图，已有选择优先于尺寸建议。新场景询问典型逻辑显示尺寸；网页填 CSS px，24 CSS px 的 2× 屏仍是 24。默认 ≤32 参考 compact，>32 参考 spacious；项目 `compact_max_size` 和显式场景映射优先。只有 original 时沿用它。缺推荐规格须报告并先取得留白生成授权，不能自动制作。
2. 同一场景的 ICO、ICNS、资源集、响应式宽度、1×/2× 和所有密度始终使用同一构图；只调整输出大小。应用图标、favicon、菜单栏/托盘分别评估，平台安全区缩放在同场景各密度保持一致。
3. 询问是否需要自带底板，选择 background 或 transparent。透明版本直接露出所在区域背景；不要按整页背景代替 Logo 区域的实际背景。
4. 询问该区域一直浅、一直深、还是随界面变化。一直浅选固定 light，一直深选固定 dark。变化时询问用途：网页推荐 adaptive，接入后实际验证 light/dark 和手动主题；设计稿、文档、图片导出、其他或未知用途必须追问**本次实际背景**，再选固定 light/dark。不要求用户判断 CSS 技术条件。
5. 固定文件为 `base/logo-{layout}-{background|transparent}-{light|dark}.svg`；明暗合一为 `base/adaptive/logo-{layout}-{background|transparent}.svg`。不存在的组合不能假定已提供，不得静默拿另一配色或另一构图替代。两种留白完整时为 8 固定 + 4 adaptive；部分资源按实际可用交付。
6. 输出所选文件的绝对路径。可用根目录 `python3 select_logo.py` 引导选择及复制，复制采用排他创建，不覆盖已有文件。脚本只需 Python 标准库。

例如：24 CSS px 导航 Logo 的同一场景在 1× 和 2× 均用 compact；64px 应用图标可用 spacious，ICNS 内 16px 条目仍保持 spacious。白色文档上的透明 Logo 选择 `base/logo-compact-transparent-light.svg`，即使操作系统是深色也不选 dark。手动切换主题的网页可选 adaptive，但需实际验证图标区域背景与颜色响应一致。

adaptive 默认 light，通过 SVG `prefers-color-scheme: dark` 仅切配色。它不能识别实际区域背景，导入工具和静态渲染可能只取默认色。网页接入者应设置合适的宿主 `color-scheme` 并验证目标浏览器；这属于实际集成验证，资源生成不能声称已完成。

## 圆角、轮廓和源文件责任

base 有底 SVG 是满幅不透明直角底板，透明版保留同一主体位置、比例和留白。源文件始终保留，不默认覆盖或归档。普通界面用显示容器的圆角和裁切；仅设 border-radius 而未裁切内容不够。推荐半径取目标项目约定；无约定时可从边长的 1/4 作为可调整建议，例如 16/24/32/48/64 px 对应 4/6/8/12/16 px，不使用专属品牌 token。

```html
<span style="display:inline-block;width:32px;height:32px;border-radius:8px;overflow:hidden">
  <img src="base/logo-compact-background-light.svg" alt="app" style="display:block;width:100%;height:100%">
</span>
```

平台文件可在导出阶段按项目轮廓配置完成圆角；已有圆角不是过期理由。系统或商店负责遮罩的 `.icon`、Apple Touch、Android adaptive、Play Store 不重复烘焙。ICNS/ICO/Linux 轮廓来自明确源和本轮导出配置，不能读取上轮平台产物来推导，因此空目标目录也可重建。
