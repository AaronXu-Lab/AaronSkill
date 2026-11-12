# 资源组 CLI 与显式映射

保留 `--source /absolute/logo.svg` 和 `--source-svg`，可重复 `--source` 或传指定目录。单文件默认 `original` 留白，单主题使用 `--theme light|dark` 明确归属；`--inspect-theme` 的背景亮度推测只是提示，不能覆盖用户语义。`--layout compact|spacious` 可显式声明留白。标准名称 `logo-compact-background-light.svg` 可以直接解析角色；非标准多文件先核实角色，写 JSON 映射（所有 path 为用户明确指定的绝对 SVG 路径）：

```json
{
  "sources": [
    {"path": "/input/compact.svg", "layout": "compact", "kind": "background", "theme": "adaptive", "background_selector": "#plate"},
    {"path": "/input/spacious-light.svg", "layout": "spacious", "kind": "background", "theme": "light"},
    {"path": "/input/spacious-dark.svg", "layout": "spacious", "kind": "background", "theme": "dark"}
  ],
  "compact_max_size": 32,
  "scenarios": {
    "favicon": {"layout": "compact", "size": 16},
    "app": {"layout": "spacious", "size": 64, "radius_fraction": 0.2},
    "status": {"layout": "compact", "size": 16}
  }
}
```

`background_selector` 只用于已经确认的独立底板（简单 #id / .class / 元素选择器，必须唯一）。不确定时先询问，不通过试删来猜测。透明输入无需底板；若需派生有底版，必须提供相同构图主题的已确认有底源。已有底板颜色和配色直接用，不维护脚本品牌调色板。

```bash
python3 scripts/cook.py --source-map /absolute/map.json --inspect-theme
python3 scripts/cook.py --source-map /absolute/map.json --project-root /absolute/output --base-only
python3 scripts/cook.py --source-map /absolute/map.json --project-root /absolute/output
python3 scripts/cook.py --source /absolute/logo.svg --project-root /absolute/output --platforms web,windows,linux,android
```

`--base-only` 交付基础资源、选择器和说明，不依赖 compose-app-icon/iconutil；仍用 rsvg-convert/Pillow 校验 SVG 渲染。`--inspect-theme` 无第三方依赖。默认全平台以兼容旧调用；缺主题时全平台停止，不能自动补色。

可选授权派生字段（AI 先评估、用户批准后才填写并传相应旗标）：

```json
{
  "sources": [{"path": "/input/logo.svg", "layout": "compact", "kind": "background", "theme": "light"}],
  "derive_layouts": [{"from": "compact", "to": "spacious", "scale": 0.8, "translate": [0, 0]}],
  "derive_themes": [{"from": "light", "to": "dark", "colors": {"#FFFFFF": "#111111", "#111111": "#FFFFFF"}}]
}
```

留白只对整体主体按 viewBox 中心缩放并平移（translate 为 viewBox 单位），底板不变；传 `--allow-padding` 表示已有同范围留白授权。补色仅替换映射中的颜色，传 `--allow-colors` 表示已有同范围补色授权。两旗标均不代表脚本替用户批准；未传时阻塞对应派生。已存在目标角色不重复生成。AI 必须实际查看派生渲染并确认未改变内部结构/原主题；像素检查不能替代配色和留白视觉判断。

目标受管文件由 `.logo-cook-managed.json` 记录（事务所有权清单，不是产品 metadata）。首次同名路径默认保护；`--replace-existing` 只用于用户已授权接管的精确生成路径。已正确放在输出路径的输入源经渲染比较后沿用原字节，不重复加工、不纳入所有权清单；不等价时选择独立输出目录。无论该旗标如何，输入源、目标 base 内未知文件和无关文件始终保护；不得先删目录。清单只记录本轮产物，未选平台和旧文件留在原位，不自动清理。
