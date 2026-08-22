#!/usr/bin/env python3
"""Inspect or cook a minimal platform icon set from an explicitly selected SVG or directory."""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


SKILL_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd().resolve()
COMPOSE_SKILL_DIR = PROJECT_ROOT / ".agents" / "skills" / "compose-app-icon"
SVG_NS = "http://www.w3.org/2000/svg"
GENERATED_DIRS = ("web", "iOS&macOS", "windows", "linux", "android")
GENERATED_ROOT_FILES = ("README.md",)
LEGACY_DIRS = ("macos", "ios")
LEGACY_FILES = ("contact-sheet.png", "ASSET-MAP.md", "skills-lock.json", "checksums.sha256")

ET.register_namespace("", SVG_NS)


def require(command: str) -> str:
    path = shutil.which(command)
    if not path:
        raise SystemExit(f"Required command not found: {command}")
    return path


def preflight_compose_skill() -> Path:
    required = (
        COMPOSE_SKILL_DIR / "SKILL.md",
        COMPOSE_SKILL_DIR / "scripts" / "validate_icon.py",
        COMPOSE_SKILL_DIR / "scripts" / "icon-schema.json",
        COMPOSE_SKILL_DIR / "scripts" / "pyproject.toml",
        COMPOSE_SKILL_DIR / "scripts" / "uv.lock",
    )
    missing = [path.relative_to(PROJECT_ROOT) for path in required if not path.is_file()]
    if missing:
        details = "\n".join(f"  - {path}" for path in missing)
        raise SystemExit(
            "Required skill compose-app-icon is missing or incomplete.\n"
            f"Expected it at: {COMPOSE_SKILL_DIR}\n"
            f"Missing files:\n{details}\n"
            "Do not generate or clean assets. Ask the user for permission to install "
            "compose-app-icon, install it after approval, then rerun this cook."
        )
    require("uv")
    return COMPOSE_SKILL_DIR / "scripts" / "validate_icon.py"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def copy_asset(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def resolve_source(raw_source: Path) -> Path:
    source = raw_source.expanduser()
    if not source.is_absolute():
        raise SystemExit("--source must be an absolute SVG or directory path explicitly supplied by the user")
    source = source.resolve()
    if source.is_dir():
        candidates = sorted(
            path.resolve()
            for path in source.iterdir()
            if path.is_file() and path.suffix.lower() == ".svg"
        )
        if not candidates:
            raise SystemExit(f"No SVG exists at the root of the explicitly selected directory: {source}")
        if len(candidates) > 1:
            choices = "\n".join(f"  - {path}" for path in candidates)
            raise SystemExit(
                "Multiple SVG files exist at the root of the explicitly selected directory. "
                "Ask the user which one is canonical, then rerun with that file:\n"
                f"{choices}"
            )
        return candidates[0]
    if not source.is_file():
        raise SystemExit(f"Explicitly selected source does not exist or is not a file/directory: {source}")
    if source.suffix.lower() != ".svg":
        raise SystemExit(f"--source must point to an SVG file or a directory whose root has one SVG: {source}")
    return source


def _extract_css_block(css: str, theme: str) -> str:
    match = re.search(
        rf"@media\s*\(\s*prefers-color-scheme\s*:\s*{theme}\s*\)\s*\{{",
        css,
        flags=re.IGNORECASE,
    )
    if not match:
        return ""
    depth = 1
    index = match.end()
    start = index
    while index < len(css) and depth:
        if css[index] == "{":
            depth += 1
        elif css[index] == "}":
            depth -= 1
        index += 1
    if depth:
        raise SystemExit(f"Canonical SVG has an unterminated prefers-color-scheme: {theme} block")
    return css[start : index - 1]


def _css_palette(css: str) -> dict[str, str]:
    patterns = {
        "ink": r"(?:^|\})\s*path(?:\.ink)?\s*\{[^}]*fill:\s*(#[0-9A-Fa-f]{6})",
        "background": r"(?:^|\})\s*path\.bg\s*\{[^}]*fill:\s*(#[0-9A-Fa-f]{6})",
        "alert": r"(?:^|\})\s*path\.alert\s*\{[^}]*fill:\s*(#[0-9A-Fa-f]{6})",
    }
    palette: dict[str, str] = {}
    for role, pattern in patterns.items():
        match = re.search(pattern, css, flags=re.DOTALL | re.IGNORECASE)
        if match:
            palette[role] = match.group(1)
    return palette


def _relative_luminance(hex_color: str) -> float:
    value = hex_color.lstrip("#")
    channels = [int(value[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def inspect_svg_palette(source: Path) -> dict[str, object]:
    root = ET.parse(source).getroot()
    css = "\n".join(
        style.text or "" for style in root.findall(f".//{{{SVG_NS}}}style")
    )
    base: dict[str, str] = {}
    for path in root.findall(f".//{{{SVG_NS}}}path"):
        classes = set(path.attrib.get("class", "").split())
        fill = path.attrib.get("fill")
        if not fill:
            continue
        if "bg" in classes:
            base["background"] = fill
        elif "alert" in classes:
            base["alert"] = fill
        elif "ink" in classes or "ink" not in base:
            base["ink"] = fill

    light_css = _css_palette(_extract_css_block(css, "light"))
    dark_css = _css_palette(_extract_css_block(css, "dark"))
    base_css = re.split(r"@media\s*\(", css, maxsplit=1, flags=re.IGNORECASE)[0]
    base = {**_css_palette(base_css), **base}
    required = {"background", "ink", "alert"}
    missing_base = required - base.keys()
    if missing_base:
        raise SystemExit(
            "Canonical SVG is missing base color roles: " + ", ".join(sorted(missing_base))
        )

    if light_css or dark_css:
        light = {**base, **light_css}
        dark = {**base, **dark_css}
        if not light_css:
            light = base
        if not dark_css:
            dark = base
        mode = "dual" if light != dark else "single-light" if _relative_luminance(base["background"]) >= 0.35 else "single-dark"
        return {"theme_mode": mode, "palettes": {"light": light, "dark": dark}}

    single_theme = "light" if _relative_luminance(base["background"]) >= 0.35 else "dark"
    return {"theme_mode": f"single-{single_theme}", "palettes": {single_theme: base}}


def svg_palette(source: Path) -> dict[str, dict[str, str]]:
    inspection = inspect_svg_palette(source)
    mode = inspection["theme_mode"]
    if mode != "dual":
        missing_theme = "dark" if mode == "single-light" else "light"
        raise SystemExit(
            f"Theme inspection result: {mode}. Do not generate or clean assets. "
            f"Tell the user that the SVG lacks a {missing_theme} theme and ask whether AI may "
            "create the complementary theme colors. If the user declines, stop. If approved, "
            "create a theme-complete SVG and rerun with that file."
        )
    return inspection["palettes"]  # type: ignore[return-value]


def variant_svg(
    source: Path,
    palette: dict[str, dict[str, str]],
    theme: str,
    *,
    foreground: bool = False,
    monochrome: str | None = None,
    full_bleed: bool = False,
    canvas: int | None = None,
) -> str:
    root = copy.deepcopy(ET.parse(source).getroot())
    style = root.find(f"{{{SVG_NS}}}style")
    if style is not None:
        root.remove(style)

    background_index = None
    for index, path in enumerate(list(root)):
        if path.tag != f"{{{SVG_NS}}}path":
            continue
        classes = set(path.attrib.get("class", "").split())
        if "bg" in classes:
            background_index = index
            if foreground or full_bleed:
                root.remove(path)
                continue
            path.set("fill", palette[theme]["background"])
        elif monochrome:
            path.set("fill", monochrome)
        elif "alert" in classes:
            path.set("fill", palette[theme]["alert"])
        else:
            path.set("fill", palette[theme]["ink"])

    if full_bleed and not foreground:
        rect = ET.Element(
            f"{{{SVG_NS}}}rect",
            {"width": "32", "height": "32", "fill": palette[theme]["background"]},
        )
        root.insert(background_index if background_index is not None else 0, rect)
    if canvas:
        root.set("width", str(canvas))
        root.set("height", str(canvas))
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode") + "\n"


def render(svg: Path, png: Path, size: int) -> None:
    png.parent.mkdir(parents=True, exist_ok=True)
    run(RSVG, "-w", str(size), "-h", str(size), "-o", str(png), str(svg))


def save_ico(source_png: Path, output: Path, sizes: list[int]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_png) as source:
        source.convert("RGBA").save(output, format="ICO", sizes=[(size, size) for size in sizes])


def force_rgba_png(path: Path) -> None:
    """Preserve an explicit alpha channel even when every pixel is fully opaque."""
    with Image.open(path) as source:
        rgba = source.convert("RGBA")
        rgba.putalpha(255)
        rgba.save(path, format="PNG")


def resized_foreground(source_png: Path, output: Path, size: int, ratio: float = 0.66) -> None:
    with Image.open(source_png) as source:
        source = source.convert("RGBA")
        inner = max(1, round(size * ratio))
        scaled = source.resize((inner, inner), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        offset = (size - inner) // 2
        canvas.alpha_composite(scaled, (offset, offset))
        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output)


def save_maskable_icon(
    foreground_png: Path,
    output: Path,
    size: int,
    background: str,
    ratio: float = 0.8,
) -> None:
    """Place the foreground inside the maskable safe zone on an opaque canvas."""
    value = background.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Maskable background must be a six-digit hex color: {background}")
    color = tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))
    with Image.open(foreground_png) as source:
        foreground = source.convert("RGBA")
        inner = max(1, round(size * ratio))
        foreground = foreground.resize((inner, inner), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (size, size), (*color, 255))
        offset = (size - inner) // 2
        canvas.alpha_composite(foreground, (offset, offset))
        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output)


def srgb(hex_color: str) -> str:
    value = hex_color.lstrip("#")
    channels = [int(value[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    return "srgb:" + ",".join(f"{channel:.10f}".rstrip("0").rstrip(".") for channel in channels) + ",1"


def clean_outputs() -> None:
    for dirname in GENERATED_DIRS + LEGACY_DIRS:
        target = PROJECT_ROOT / dirname
        if target.is_dir():
            shutil.rmtree(target)
    for filename in GENERATED_ROOT_FILES + LEGACY_FILES:
        target = PROJECT_ROOT / filename
        if target.is_file():
            target.unlink()


def write_pwa_manifest(root: Path) -> None:
    write_json(
        root / "manifest.webmanifest",
        {
            "icons": [
                {
                    "src": "icon-192.png",
                    "type": "image/png",
                    "sizes": "192x192",
                    "purpose": "any",
                },
                {
                    "src": "icon-512.png",
                    "type": "image/png",
                    "sizes": "512x512",
                    "purpose": "any",
                },
                {
                    "src": "icon-maskable-512.png",
                    "type": "image/png",
                    "sizes": "512x512",
                    "purpose": "maskable",
                },
            ]
        },
    )


def write_usage_readme(source: Path) -> None:
    write_text(
        PROJECT_ROOT / "README.md",
        f"""# 应用图标资源使用说明

本目录由唯一事实源 `{source.name}` 生成。除更新该 SVG 外，不要直接编辑平台产物；源文件变化后应重新运行图标生成 SKILL。

## Web

- `web/favicon.svg`：现代浏览器首选 favicon，保留 SVG 内部的明暗主题切换。部署后通过 `<link rel=\"icon\" type=\"image/svg+xml\">` 引用。
- `web/favicon.ico`：旧浏览器及 `/favicon.ico` 约定的兼容回退，包含常用小尺寸。
- `web/apple-touch-icon.png`：iOS/iPadOS 网页添加到主屏幕时使用。它是满幅不透明方图，不要再次预制圆角。
- `web/pwa/icon-192.png` 与 `web/pwa/icon-512.png`：PWA 的普通应用图标。
- `web/pwa/icon-maskable-512.png`：PWA maskable 图标，背景满幅且主体位于安全区。
- `web/pwa/manifest.webmanifest`：只声明上述三张 PWA 图标。若产品已有 manifest，应合并 `icons`，不要覆盖名称、启动路径、显示模式、范围或主题色；网页仍需通过 `<link rel=\"manifest\">` 引用最终 manifest URL。

## iOS 与 macOS

- `iOS&macOS/app.icon`：iOS 与 macOS 共用的 Icon Composer 应用图标包，包含 Default、Dark 与 Tinted/Mono 外观。通过 Xcode 或 Icon Composer 加入应用图标配置，不要转换为 `.icns` 代替。
- `iOS&macOS/menu-bar/appTemplate.svg`：macOS 菜单栏 Template Image 的矢量源，由系统按当前外观着色。
- `iOS&macOS/menu-bar/appTemplate.png` 与 `appTemplate@2x.png`：分别用于 1x/2x 菜单栏位图接入。加载后应标记为 template image，不要作为全彩应用图标使用。

## Windows

- `windows/app.ico`：用于应用可执行文件、安装器、快捷方式及窗口图标，内含多种尺寸。
- `windows/tray-light.ico`：用于浅色系统主题或浅色托盘背景，图形采用深色前景。
- `windows/tray-dark.ico`：用于深色系统主题或深色托盘背景，图形采用浅色前景。应用应监听系统主题并选择对应文件。

## Linux

- `linux/app.svg`：可缩放应用图标，并保留 SVG 明暗主题行为。优先作为桌面集成的矢量源；若目标桌面或打包格式要求固定 PNG 尺寸，应在集成阶段从该 SVG 渲染，不要反向编辑生成文件。

## Android

- `android/res/`：自适应启动图标资源。将所需文件合并到应用模块的 `src/main/res/`，不要覆盖项目中无关资源。
- `mipmap-anydpi-v26/ic_launcher.xml` 与 `ic_launcher_round.xml`：自适应图标入口，引用背景、前景与 monochrome 图层。
- 各密度 `ic_launcher_foreground.png`：自适应前景；各密度 `ic_launcher_monochrome.png`：Android 主题图标遮罩；`ic_launcher.png`：旧版本回退。
- `android/play-store-512.png`：提交 Google Play Console 的 512×512 商店图。它是满幅、无预制圆角的 32-bit RGBA PNG；Alpha 通道存在且所有像素均为 255，由商店负责最终遮罩与阴影。

## 集成边界

这些文件是资源交付，不会自动修改产品仓库的 HTML、manifest、Xcode、Windows 打包、Linux desktop entry 或 Android Gradle 配置。接入时应遵循目标项目现有结构，并合并而不是覆盖既有产品元数据。
""",
    )


def cook_web(
    source: Path,
    build: Path,
    palette: dict[str, dict[str, str]],
    light_png: Path,
) -> None:
    root = PROJECT_ROOT / "web"
    copy_asset(source, root / "favicon.svg")
    save_ico(light_png, root / "favicon.ico", [16, 32, 48])
    render(build / "full-bleed-light.svg", root / "apple-touch-icon.png", 180)
    render(build / "full-light.svg", root / "pwa" / "icon-192.png", 192)
    render(build / "full-light.svg", root / "pwa" / "icon-512.png", 512)
    foreground_png = build / "web-foreground-1024.png"
    render(build / "foreground-light.svg", foreground_png, 1024)
    save_maskable_icon(
        foreground_png,
        root / "pwa" / "icon-maskable-512.png",
        512,
        palette["light"]["background"],
    )
    write_pwa_manifest(root / "pwa")


def cook_apple(build: Path, palette: dict[str, dict[str, str]], validator: Path) -> None:
    root = PROJECT_ROOT / "iOS&macOS"
    package = root / "app.icon"
    assets = package / "Assets"
    assets.mkdir(parents=True, exist_ok=True)
    copy_asset(build / "foreground-light.svg", assets / "foreground-light.svg")
    copy_asset(build / "foreground-dark.svg", assets / "foreground-dark.svg")
    copy_asset(build / "foreground-mono.svg", assets / "foreground-mono.svg")
    write_json(
        package / "icon.json",
        {
            "fill-specializations": [
                {"value": {"solid": srgb(palette["light"]["background"])}},
                {"appearance": "dark", "value": {"solid": srgb(palette["dark"]["background"])}},
            ],
            "groups": [
                {
                    "layers": [
                        {
                            "name": "app foreground",
                            "image-name-specializations": [
                                {"value": "foreground-light.svg"},
                                {"appearance": "dark", "value": "foreground-dark.svg"},
                                {"appearance": "tinted", "value": "foreground-mono.svg"},
                            ],
                            "glass": False,
                        }
                    ],
                    "shadow": {"kind": "none", "opacity": 0},
                    "translucency": {"enabled": False, "value": 0},
                }
            ],
            "supported-platforms": {"squares": "shared"},
        },
    )

    menu_svg = build / "status-template.svg"
    copy_asset(menu_svg, root / "menu-bar" / "appTemplate.svg")
    render(menu_svg, root / "menu-bar" / "appTemplate.png", 16)
    render(menu_svg, root / "menu-bar" / "appTemplate@2x.png", 32)

    compose_scripts = validator.parent
    run("uv", "sync", cwd=compose_scripts)
    result = run("uv", "run", "python", validator.name, str(package), cwd=compose_scripts)
    print(result.stdout.strip())

    ictool_candidates: list[Path] = []
    if shutil.which("xcode-select"):
        try:
            developer = Path(run("xcode-select", "-p").stdout.strip())
            ictool_candidates.append(developer.parent / "Applications" / "Icon Composer.app" / "Contents" / "Executables" / "ictool")
        except subprocess.CalledProcessError:
            pass
    ictool_candidates.append(Path("/Applications/Icon Composer.app/Contents/Executables/ictool"))
    ictool = next((path for path in ictool_candidates if path.is_file()), None)
    if not ictool:
        print("SKIPPED .icon engine validation: Icon Composer ictool unavailable")
        return
    renditions = ("Default", "Dark", "TintedLight", "TintedDark", "ClearLight", "ClearDark")
    for platform in ("iOS", "macOS"):
        for rendition in renditions:
            run(
                str(ictool),
                str(package),
                "--export-image",
                "--output-file",
                str(build / f"{platform}-{rendition}.png"),
                "--platform",
                platform,
                "--rendition",
                rendition,
                "--width",
                "1024",
                "--height",
                "1024",
                "--scale",
                "1",
            )
    print("Icon Composer rendered iOS/macOS Default, Dark, Mono, and Clear successfully")


def cook_windows(build: Path, light_png: Path) -> None:
    root = PROJECT_ROOT / "windows"
    save_ico(light_png, root / "app.ico", [16, 24, 32, 48, 64, 128, 256])
    for theme in ("light", "dark"):
        tray_png = build / f"tray-{theme}-256.png"
        render(build / f"status-{theme}.svg", tray_png, 256)
        save_ico(tray_png, root / f"tray-{theme}.ico", [16, 20, 24, 32])


def cook_linux(source: Path) -> None:
    copy_asset(source, PROJECT_ROOT / "linux" / "app.svg")


def cook_android(build: Path, palette: dict[str, dict[str, str]]) -> None:
    root = PROJECT_ROOT / "android"
    res = root / "res"
    densities = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    foreground_sizes = {name: size * 3 for name, size in densities.items()}
    foreground_master = build / "foreground-light-1024.png"
    mono_master = build / "monochrome-1024.png"
    render(build / "foreground-light.svg", foreground_master, 1024)
    render(build / "status-template.svg", mono_master, 1024)

    for density, size in densities.items():
        render(build / "full-light.svg", res / f"mipmap-{density}" / "ic_launcher.png", size)
    for density, size in foreground_sizes.items():
        resized_foreground(foreground_master, res / f"mipmap-{density}" / "ic_launcher_foreground.png", size)
        resized_foreground(mono_master, res / f"mipmap-{density}" / "ic_launcher_monochrome.png", size)

    adaptive = """<adaptive-icon xmlns:android=\"http://schemas.android.com/apk/res/android\">\n  <background android:drawable=\"@color/ic_launcher_background\" />\n  <foreground android:drawable=\"@mipmap/ic_launcher_foreground\" />\n  <monochrome android:drawable=\"@mipmap/ic_launcher_monochrome\" />\n</adaptive-icon>\n"""
    write_text(res / "mipmap-anydpi-v26" / "ic_launcher.xml", adaptive)
    write_text(res / "mipmap-anydpi-v26" / "ic_launcher_round.xml", adaptive)
    write_text(
        res / "values" / "colors.xml",
        f"<resources>\n  <color name=\"ic_launcher_background\">{palette['light']['background']}</color>\n</resources>\n",
    )
    play_store = root / "play-store-512.png"
    render(build / "full-bleed-light.svg", play_store, 512)
    force_rgba_png(play_store)


def main() -> None:
    global COMPOSE_SKILL_DIR, PROJECT_ROOT, RSVG
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Absolute path to the favicon-package project root; required when cooking",
    )
    parser.add_argument(
        "--source",
        "--source-svg",
        dest="source",
        required=True,
        type=Path,
        help="Absolute path to the SVG or resource directory explicitly selected by the user",
    )
    parser.add_argument(
        "--inspect-theme",
        action="store_true",
        help="Print theme inspection JSON without checking dependencies or changing outputs",
    )
    args = parser.parse_args()
    source = resolve_source(args.source)
    inspection = inspect_svg_palette(source)
    if args.inspect_theme:
        print(json.dumps({"source": str(source), **inspection}, indent=2, ensure_ascii=False))
        return
    if args.project_root is None:
        raise SystemExit("--project-root is required when cooking assets")
    project_root = args.project_root.expanduser()
    if not project_root.is_absolute():
        raise SystemExit("--project-root must be an absolute path")
    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise SystemExit(f"Project root does not exist or is not a directory: {project_root}")
    PROJECT_ROOT = project_root
    COMPOSE_SKILL_DIR = PROJECT_ROOT / ".agents" / "skills" / "compose-app-icon"
    palette = svg_palette(source)
    validator = preflight_compose_skill()
    RSVG = require("rsvg-convert")
    clean_outputs()

    with tempfile.TemporaryDirectory(prefix="app-logo-cook-") as temp:
        build = Path(temp)
        for theme in ("light", "dark"):
            write_text(build / f"full-{theme}.svg", variant_svg(source, palette, theme))
            write_text(
                build / f"foreground-{theme}.svg",
                variant_svg(source, palette, theme, foreground=True, canvas=1024),
            )
            write_text(
                build / f"status-{theme}.svg",
                variant_svg(source, palette, theme, foreground=True, monochrome=palette[theme]["ink"]),
            )
        write_text(
            build / "full-bleed-light.svg",
            variant_svg(source, palette, "light", full_bleed=True),
        )
        write_text(
            build / "foreground-mono.svg",
            variant_svg(source, palette, "light", foreground=True, monochrome="#FFFFFF", canvas=1024),
        )
        write_text(
            build / "status-template.svg",
            variant_svg(source, palette, "light", foreground=True, monochrome="#000000"),
        )
        light_png = build / "full-light-1024.png"
        render(build / "full-light.svg", light_png, 1024)
        cook_web(source, build, palette, light_png)
        cook_apple(build, palette, validator)
        cook_windows(build, light_png)
        cook_linux(source)
        cook_android(build, palette)
        write_usage_readme(source)

    print(f"Cooked minimal app assets from {source.name}")


if __name__ == "__main__":
    main()
