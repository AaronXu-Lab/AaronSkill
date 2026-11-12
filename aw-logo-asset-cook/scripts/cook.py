#!/usr/bin/env python3
"""Inspect or cook a minimal platform icon set from an explicitly selected SVG or directory."""

from __future__ import annotations

import argparse
import copy
import json
import hashlib
import os
import sys
import shutil
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Inspection and the delivered selector do not require platform dependencies.
try:
    from PIL import Image
except ImportError:
    Image = None

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resources as resources


SKILL_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd().resolve()
COMPOSE_SKILL_DIR = PROJECT_ROOT / ".agents" / "skills" / "compose-app-icon"
SVG_NS = "http://www.w3.org/2000/svg"

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
            "Apple .icon generation requires compose-app-icon, which is missing or incomplete.\n"
            f"Expected it at: {COMPOSE_SKILL_DIR}\n"
            f"Missing files:\n{details}\n"
            "No requested output has been changed. Base-only and --platforms web,windows,linux,android do not need this Apple dependency. Ask permission to install "
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
    """Compatibility helper for callers that explicitly need one file."""
    entries = resources.entries_for_sources([raw_source])
    if len(entries) != 1:
        raise SystemExit("Multiple role-mapped resources; use the resource-group interface")
    return Path(entries[0]["path"])


def inspect_svg_palette(source: Path) -> dict[str, object]:
    entries = resources.entries_for_sources([source])
    records, backgrounds, _ = resources.collect({"sources": entries})
    entry = entries[0]
    palettes = {}
    for theme in resources.THEMES:
        key = entry["layout"], entry["kind"], theme
        if key not in records:
            continue
        original = resources.parse(source)
        frozen = resources.freeze(original, theme)
        colors = [e.get("fill") for e in frozen.iter() if resources.tag(e) in resources.SHAPES]
        bg = backgrounds.get((entry["layout"], theme))
        foreground = [c for c in colors if c != bg and c != "none"]
        palettes[theme] = {"background": bg, "ink": foreground[0] if foreground else "#000000"}
        if len(foreground) > 1:
            palettes[theme]["alert"] = foreground[1]
    mode = "dual" if entry["theme"] == "adaptive" else "single-" + entry["theme"]
    return {"theme_mode": mode, "palettes": palettes}


def svg_palette(source: Path) -> dict[str, dict[str, str]]:
    inspection = inspect_svg_palette(source)
    if inspection["theme_mode"] != "dual":
        raise SystemExit("Do not generate or clean assets. Single theme requires explicit complementary-color authorization and a reviewed theme-complete source")
    return inspection["palettes"]


def variant_svg(source, palette, theme, *, foreground=False, monochrome=None,
                full_bleed=False, canvas=None):
    # Retain the public helper while resolving groups, rects and arbitrary viewBox.
    root, _ = resources.normalize(source, theme, "transparent" if foreground else "background")
    if monochrome:
        root = monochrome_root(root, monochrome)
    if canvas:
        root.set("width", str(canvas))
        root.set("height", str(canvas))
    return resources.serialize(root)


def monochrome_root(root, paint):
    root = copy.deepcopy(root)
    for element in root.iter():
        for key in ("opacity", "fill-opacity", "stroke-opacity"):
            if key in element.attrib:
                element.set(key, "1")
        for key in ("fill", "stroke"):
            if element.get(key) != "none":
                element.set(key, paint)
    return root


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


def verify_safe_circle(image, diameter_fraction):
    rgba = image.convert("RGBA")
    center = rgba.width / 2
    radius = rgba.width * diameter_fraction / 2
    alpha = rgba.getchannel("A")
    if not alpha.getbbox():
        raise ValueError("Safe-zone foreground is empty")
    for y in range(rgba.height):
        for x in range(rgba.width):
            if alpha.getpixel((x, y)) and (x + .5 - center) ** 2 + (y + .5 - center) ** 2 > radius ** 2:
                raise ValueError("Visible foreground extends outside the platform safe circle")


def safe_foreground(source_png, size, diameter_fraction):
    """Scale actual visible pixels, then verify every antialiased edge pixel."""
    with Image.open(source_png) as source:
        source = source.convert("RGBA")
    bounds = source.getchannel("A").getbbox()
    if not bounds:
        raise ValueError("Foreground is empty")
    # A bounding square inside the safe circle is conservative for every shape.
    # Measure the visible bounds, not a canvas that might already contain padding.
    foreground = source.crop(bounds)
    edge = max(1, int(size * diameter_fraction / 2 ** .5 * .98))
    scale = edge / max(foreground.size)
    foreground = foreground.resize((max(1, round(foreground.width * scale)), max(1, round(foreground.height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(foreground, ((size - foreground.width)//2, (size - foreground.height)//2))
    verify_safe_circle(canvas, diameter_fraction)
    return canvas


def resized_foreground(source_png, output, size, ratio=2/3):
    result = safe_foreground(source_png, size, ratio)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


def save_maskable_icon(foreground_png, output, size, background, ratio=.8):
    foreground = safe_foreground(foreground_png, size, ratio)
    color = tuple(int(background[i:i+2], 16) for i in (1, 3, 5))
    canvas = Image.new("RGBA", (size, size), (*color, 255))
    canvas.alpha_composite(foreground)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def srgb(hex_color: str) -> str:
    value = hex_color.lstrip("#")
    channels = [int(value[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    return "srgb:" + ",".join(f"{channel:.10f}".rstrip("0").rstrip(".") for channel in channels) + ",1"


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


def write_usage_readme(config, records, platforms):
    rules = (SKILL_DIR / "references" / "selection.md").read_text(encoding="utf-8")
    inventory = "\n".join(f"- `base/{resources.filename(key)}`" for key in sorted(records))
    scenarios = {name: resources.choose_layout(records, name, config) for name in ("app", "favicon", "status")}
    mapping = "\n".join(f"- {name}: {layout}" for name, layout in scenarios.items())
    write_text(PROJECT_ROOT / "base" / "README.md", "# 基础 Logo 规则\n\n" + rules + "\n## 实际固定资源\n\n" + inventory + "\n")
    platform_rules = (SKILL_DIR / "references" / "platform-validation.md").read_text(encoding="utf-8")
    usage = """## 平台接入方式

- Web：用 `<link rel="icon" type="image/svg+xml" href="web/favicon.svg">`；旧环境用 web/favicon.ico。web/apple-touch-icon.png 用于网页添加主屏幕；web/pwa/manifest.webmanifest 的 icons 合并进现有 manifest 后以 link rel="manifest" 引用，不覆盖产品名称或启动配置。
- iOS/macOS：将 iOS&macOS/app.icon 加入 Xcode / Icon Composer 图标配置；传统 iOS&macOS/app.icns 放应用包 Contents/Resources，以 CFBundleIconFile 引用，或用打包工具对应配置。两格式并存。iOS&macOS/menu-bar/appTemplate.svg、appTemplate.png、appTemplate@2x.png 加载后标为 template image，由系统着色。
- Windows：windows/app.ico 用于 exe、安装器、窗口或快捷方式。按实际托盘背景选择 windows/tray-light.ico / windows/tray-dark.ico，并监听外观变化。
- Linux：linux/app.svg 用于 desktop entry 或对应打包配置；必要时从该 SVG 渲染固定尺寸 PNG，不编辑生成文件后反向继承。
- Android：将 android/res/ 中本次资源合并到应用模块 src/main/res，adaptive XML 引用背景、foreground、monochrome；不要覆盖无关资源。android/play-store-512.png 用于商店提交。

资源生成不修改 HTML、manifest、Xcode、desktop entry、Gradle 或打包配置。只按下列本次平台清单使用；未列平台未在本次生成。实际文件列表以受管清单为准。
"""
    write_text(PROJECT_ROOT / "README.md", "# 应用图标资源使用说明\n\n" + rules + "\n## 本次场景映射\n\n" + mapping + "\n\n本次生成平台：" + (", ".join(platforms) or "仅基础资源") + "\n\n" + usage + "\n" + platform_rules)
    template = (SKILL_DIR / "scripts" / "select_logo.py").read_text(encoding="utf-8")
    selector_config = {k: config[k] for k in ("scenarios", "compact_max_size") if k in config}
    write_text(PROJECT_ROOT / "select_logo.py", template.replace("CONFIG = {}", "CONFIG = " + repr(selector_config)))


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


def normalize_legacy_icns(output: Path, iconset: Path) -> None:
    """Use classic RGB + mask chunks for small icons, avoiding ic04/ic05 ARGB drift."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">4sI", kind, len(data) + 8) + data

    data = output.read_bytes()
    parts = []
    offset = 8
    while offset < len(data):
        kind, length = struct.unpack(">4sI", data[offset:offset + 8])
        if length < 8 or offset + length > len(data):
            raise ValueError("Malformed ICNS chunk")
        if kind not in (b"ic04", b"ic05", b"is32", b"il32", b"s8mk", b"l8mk"):
            parts.append(data[offset:offset + length])
        offset += length
    for size, rgb_kind, alpha_kind in ((16, b"is32", b"s8mk"), (32, b"il32", b"l8mk")):
        with Image.open(iconset / f"icon_{size}x{size}.png") as image:
            rgba = image.convert("RGBA")
            encoded = bytearray()
            for channel in rgba.split()[:3]:
                raw = channel.tobytes()
                # Literal RLE packets; a trailing pad accommodates Apple's decoder lookahead.
                for start in range(0, len(raw), 127):
                    block = raw[start:start + 127]
                    encoded.append(len(block) - 1)
                    encoded.extend(block)
            encoded.append(0)
            parts.append(chunk(rgb_kind, bytes(encoded)))
            parts.append(chunk(alpha_kind, rgba.getchannel("A").tobytes()))
    output.write_bytes(chunk(b"icns", b"".join(parts)))


def cook_macos_legacy(build: Path) -> None:
    """Compile the complete Retina iconset and verify the ICNS round trip."""
    iconutil = require("iconutil")
    iconset = build / "app.iconset"
    expected: dict[str, int] = {}
    for points in (16, 32, 128, 256, 512):
        for scale in (1, 2):
            suffix = "@2x" if scale == 2 else ""
            name = f"icon_{points}x{points}{suffix}.png"
            expected[name] = points * scale
            render(build / "full-light.svg", iconset / name, points * scale)
    output = PROJECT_ROOT / "iOS&macOS" / "app.icns"
    output.parent.mkdir(parents=True, exist_ok=True)
    run(iconutil, "-c", "icns", str(iconset), "-o", str(output))
    normalize_legacy_icns(output, iconset)
    unpacked = build / "roundtrip.iconset"
    run(iconutil, "-c", "iconset", str(output), "-o", str(unpacked))
    for name, size in expected.items():
        with Image.open(iconset / name) as source, Image.open(unpacked / name) as decoded:
            if decoded.size != (size, size):
                raise ValueError(f"ICNS size mismatch: {name}: {decoded.size}")
            if source.convert("RGBA").tobytes() != decoded.convert("RGBA").tobytes():
                raise ValueError(f"ICNS pixel mismatch: {name}")
    print("ICNS round-trip verified: all ten standard/Retina images, 16–1024 pixels")


def write_apple_package(build: Path, palette: dict[str, dict[str, str]]) -> Path:
    root = PROJECT_ROOT / "iOS&macOS"
    package = root / "app.icon"
    assets = package / "Assets"
    assets.mkdir(parents=True, exist_ok=True)
    for theme in ('light', 'dark', 'mono'):
        foreground = ET.parse(build / f'foreground-{theme}.svg').getroot()
        foreground.set('width', '1024')
        foreground.set('height', '1024')
        write_text(assets / f'foreground-{theme}.svg', resources.serialize(foreground))
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

    return package


def validate_icon_engine(package: Path, build: Path) -> bool:
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
        return False
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
            output = build / f"{platform}-{rendition}.png"
            with Image.open(output) as image:
                if image.size != (1024, 1024) or not image.convert('RGBA').getchannel('A').getbbox():
                    raise ValueError(f'Icon Composer produced an empty or wrong-sized render: {platform}/{rendition}')
    print("Icon Composer rendered iOS/macOS Default, Dark, Mono, and Clear successfully")
    return True


def cook_apple(build: Path, palette: dict[str, dict[str, str]], validator: Path) -> None:
    root = PROJECT_ROOT / "iOS&macOS"
    package = write_apple_package(build, palette)
    menu_svg = build / "status-template.svg"
    copy_asset(menu_svg, root / "menu-bar" / "appTemplate.svg")
    render(menu_svg, root / "menu-bar" / "appTemplate.png", 16)
    render(menu_svg, root / "menu-bar" / "appTemplate@2x.png", 32)

    compose_scripts = validator.parent
    run("uv", "sync", cwd=compose_scripts)
    result = run("uv", "run", "python", validator.name, str(package), cwd=compose_scripts)
    print(result.stdout.strip())

    validate_icon_engine(package, build)


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
    render(build / "foreground-mono.svg", mono_master, 1024)

    for density, size in densities.items():
        render(build / "unrounded-light.svg", res / f"mipmap-{density}" / "ic_launcher.png", size)
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


def validate_platform_files(stage, platforms):
    expected = {}
    if 'web' in platforms:
        expected.update({'web/apple-touch-icon.png':180, 'web/pwa/icon-192.png':192,
                         'web/pwa/icon-512.png':512, 'web/pwa/icon-maskable-512.png':512})
    if 'apple' in platforms:
        expected.update({'iOS&macOS/menu-bar/appTemplate.png':16, 'iOS&macOS/menu-bar/appTemplate@2x.png':32})
    if 'android' in platforms:
        expected['android/play-store-512.png'] = 512
        for density, size in {'mdpi':48, 'hdpi':72, 'xhdpi':96, 'xxhdpi':144, 'xxxhdpi':192}.items():
            for suffix in ('', '_foreground', '_monochrome'):
                expected[f'android/res/mipmap-{density}/ic_launcher{suffix}.png'] = size * (3 if suffix else 1)
    for relative, size in expected.items():
        with Image.open(stage / relative) as image:
            if image.size != (size, size):
                raise ValueError(f'Wrong raster size: {relative}')
            rgba = image.convert('RGBA')
            if not rgba.getchannel('A').getbbox():
                raise ValueError(f'Empty raster: {relative}')
            if relative in ('web/apple-touch-icon.png', 'web/pwa/icon-maskable-512.png', 'android/play-store-512.png'):
                if rgba.getchannel('A').getextrema() != (255, 255):
                    raise ValueError(f'Expected fully opaque raster: {relative}')
            if relative == 'android/play-store-512.png' and (image.mode != 'RGBA' or (stage/relative).read_bytes()[25] != 6):
                raise ValueError('Play Store PNG must retain its explicit alpha channel')
            if relative.endswith(('_foreground.png', '_monochrome.png')):
                verify_safe_circle(rgba, 2/3)
            if 'appTemplate' in relative or relative.endswith('_monochrome.png'):
                expected_color = (0, 0, 0) if 'appTemplate' in relative else (255, 255, 255)
                if any(pixel[:3] != expected_color for pixel in (rgba.get_flattened_data() if hasattr(rgba, "get_flattened_data") else rgba.getdata()) if pixel[3]):
                    raise ValueError(f'Status/Mono image is not monochrome: {relative}')
    icos = {}
    if 'web' in platforms:
        icos['web/favicon.ico'] = (16, 32, 48)
    if 'windows' in platforms:
        icos.update({'windows/app.ico':(16,24,32,48,64,128,256), 'windows/tray-light.ico':(16,20,24,32), 'windows/tray-dark.ico':(16,20,24,32)})
    for relative, sizes in icos.items():
        with Image.open(stage / relative) as image:
            if image.info['sizes'] != {(size,size) for size in sizes}:
                raise ValueError(f'ICO sizes mismatch: {relative}')
            for size in sizes:
                decoded = image.ico.getimage((size,size)).convert('RGBA')
                if not decoded.getchannel('A').getbbox():
                    raise ValueError(f'Empty ICO entry: {relative}/{size}')
                if 'tray-' in relative:
                    paint = (0,0,0) if 'tray-light' in relative else (255,255,255)
                    if any(pixel[:3] != paint for pixel in (decoded.get_flattened_data() if hasattr(decoded, "get_flattened_data") else decoded.getdata()) if pixel[3]):
                        raise ValueError(f'Tray entry is not monochrome: {relative}/{size}')


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish(stage, target, sources, replace_existing=False):
    """Publish only validated files; preserve unknown files and roll back errors."""
    manifest_name = ".logo-cook-managed.json"
    manifest = target / manifest_name
    if manifest.is_symlink():
        raise SystemExit(f'Refusing symlink manifest: {manifest}')
    previous = json.loads(manifest.read_text()) if manifest.is_file() else {}
    if not isinstance(previous, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in previous.items()):
        raise SystemExit('Invalid ownership manifest; preserve target and review')
    files = sorted(path for path in stage.rglob("*") if path.is_file() and path.name != manifest_name)
    for path in files:
        relative = path.relative_to(stage)
        destination = target / relative
        for parent in (destination, *destination.parents):
            if parent.is_symlink():
                raise SystemExit(f"Refusing symlink target: {parent}")
            if parent == target:
                break
        if destination.resolve() in sources:
            raise SystemExit(f"Protected input source conflicts with generated path: {destination}")
        if destination.exists():
            if not destination.is_file():
                raise SystemExit(f"Output conflicts with directory: {destination}")
            old_hash = previous.get(str(relative))
            if old_hash and hash_file(destination) != old_hash:
                raise SystemExit(f"Managed file has local edits; preserve and review: {destination}")
            if not old_hash and not replace_existing:
                raise SystemExit(f"Unmanaged file protected: {destination}; explicit path takeover requires --replace-existing")
    # Retain ownership of untouched platforms, but never delete stale files.
    updated = {relative: digest for relative, digest in previous.items() if (target / relative).resolve() not in sources}
    for path in files:
        updated[str(path.relative_to(stage))] = hash_file(path)
    write_json(stage / manifest_name, updated)
    files.append(stage / manifest_name)
    with tempfile.TemporaryDirectory(prefix="logo-cook-backup-") as temp:
        backup = Path(temp)
        applied, created_dirs = [], []
        try:
            for path in files:
                relative = path.relative_to(stage)
                destination = target / relative
                if destination.exists():
                    copy_asset(destination, backup / relative)
                missing = []
                parent = destination.parent
                while not parent.exists():
                    missing.append(parent)
                    parent = parent.parent
                for parent in reversed(missing):
                    parent.mkdir()
                    created_dirs.append(parent)
                applied.append(relative)
                # Same-directory temporary file permits atomic individual replacement.
                with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as handle:
                    temporary = Path(handle.name)
                try:
                    shutil.copy2(path, temporary)
                    os.replace(temporary, destination)
                finally:
                    temporary.unlink(missing_ok=True)
        except BaseException:
            for relative in reversed(applied):
                destination = target / relative
                if (backup / relative).exists():
                    shutil.copy2(backup / relative, destination)
                else:
                    destination.unlink(missing_ok=True)
            for directory in reversed(created_dirs):
                directory.rmdir()
            raise


def preserve_in_place_sources(stage, target, sources, build):
    """Use an already-correct source at its output path without changing its bytes."""
    for output in list(stage.rglob('*.svg')):
        destination = (target / output.relative_to(stage)).resolve()
        if destination not in sources:
            continue
        original_png, normalized_png = build / 'original-in-place.png', build / 'normalized-in-place.png'
        render(destination, original_png, 256)
        render(output, normalized_png, 256)
        if pixels(original_png) != pixels(normalized_png):
            raise SystemExit(f'Protected source requires normalization at the same output path; choose a separate output directory: {destination}')
        output.unlink()  # only the temporary duplicate; the original is untouched
        print(f'Preserved existing source in place: {destination}')


def pixels(path):
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        return rgba.size, rgba.tobytes()


def validate_base(stage, build, records):
    """Real SVG renderer verifies background coverage and adaptive parity."""
    adaptive_count = 0
    for key, root in records.items():
        fixed = stage / "base" / resources.filename(key)
        write_text(fixed, resources.serialize(root))
        png = build / (fixed.stem + '.png')
        render(fixed, png, 128)
        if key[1] == 'background':
            with Image.open(png) as image:
                if image.convert('RGBA').getchannel('A').getextrema() != (255, 255):
                    raise ValueError(f'Base background is not full-bleed opaque: {key}')
    for layout, kind in sorted({key[:2] for key in records}):
        light, dark = records.get((layout, kind, 'light')), records.get((layout, kind, 'dark'))
        if light is None or dark is None:
            continue
        combined = resources.adaptive(light, dark)
        if combined is None:
            print(f'No lossless adaptive available: {layout}/{kind}; fixed themes retained')
            continue
        output = stage / 'base' / 'adaptive' / f'logo-{layout}-{kind}.svg'
        write_text(output, resources.serialize(combined))
        for theme in resources.THEMES:
            frozen = build / f'adaptive-{layout}-{kind}-{theme}.svg'
            write_text(frozen, resources.serialize(resources.freeze(combined, theme)))
            png = frozen.with_suffix('.png')
            render(frozen, png, 128)
            if pixels(png) != pixels(build / f'logo-{layout}-{kind}-{theme}.png'):
                raise ValueError(f'Adaptive/fixed render mismatch: {layout}/{kind}/{theme}')
        adaptive_count += 1
    print(f'Base validated: {len(records)} fixed, {adaptive_count} adaptive')


def platform_plan(records, backgrounds, config, platforms):
    layouts = {name: resources.choose_layout(records, name, config) for name in ('app', 'favicon', 'status')}
    needed = {layouts['app']}
    if 'web' in platforms:
        needed.add(layouts['favicon'])
    if 'apple' in platforms or 'windows' in platforms:
        needed.add(layouts['status'])
    for layout in needed:
        for theme in resources.THEMES:
            if (layout, 'transparent', theme) not in records:
                raise SystemExit(f'Do not generate or clean assets. Missing {layout}/{theme} foreground; complementary-color generation requires explicit authorization')
    if set(platforms) & {'web', 'apple', 'android'}:
        for theme in resources.THEMES:
            if (layouts['app'], theme) not in backgrounds:
                raise SystemExit(f'Do not generate or clean assets. Missing confirmed {theme} app background for the requested platform scope')
    return layouts


def build_platforms(stage, build, records, backgrounds, config, platforms, validator):
    layouts = platform_plan(records, backgrounds, config, platforms)
    print('Scenario compositions: ' + json.dumps(layouts))
    app, favicon, status = (layouts[n] for n in ('app', 'favicon', 'status'))
    palette = {theme: {'background': backgrounds.get((app, theme))} for theme in resources.THEMES}
    radius = float(config.get('scenarios', {}).get('app', {}).get('radius_fraction', 0))
    for theme in resources.THEMES:
        root = records.get((app, 'background', theme), records[app, 'transparent', theme])
        write_text(build / f'unrounded-{theme}.svg', resources.serialize(root))
        write_text(build / f'full-{theme}.svg', resources.serialize(resources.rounded(root, radius)))
        write_text(build / f'foreground-{theme}.svg', resources.serialize(records[app, 'transparent', theme]))
        if 'apple' in platforms or 'windows' in platforms:
            write_text(build / f'status-{theme}.svg', resources.serialize(monochrome_root(records[status, 'transparent', theme], '#000000' if theme == 'light' else '#FFFFFF')))
    write_text(build / 'full-bleed-light.svg', resources.serialize(records.get((app, 'background', 'light'), records[app, 'transparent', 'light'])))
    write_text(build / 'foreground-mono.svg', resources.serialize(monochrome_root(records[app, 'transparent', 'light'], '#FFFFFF')))
    if 'apple' in platforms or 'windows' in platforms:
        write_text(build / 'status-template.svg', resources.serialize(monochrome_root(records[status, 'transparent', 'light'], '#000000')))
    light_png = build / 'full-light-1024.png'
    render(build / 'full-light.svg', light_png, 1024)
    if 'web' in platforms:
        favicon_kind = 'background' if (favicon, 'background', 'light') in records else 'transparent'
        adaptive = stage / 'base' / 'adaptive' / f'logo-{favicon}-{favicon_kind}.svg'
        if not adaptive.is_file():
            raise SystemExit('Web favicon needs a lossless adaptive resource; clarify differing theme geometry')
        favicon_png = build / 'favicon-light-256.png'
        render(stage / 'base' / resources.filename((favicon, 'background' if (favicon, 'background', 'light') in records else 'transparent', 'light')), favicon_png, 256)
        cook_web(adaptive, build, palette, favicon_png)
    if 'apple' in platforms:
        cook_macos_legacy(build)
        cook_apple(build, palette, validator)
    if 'windows' in platforms:
        cook_windows(build, light_png)
    if 'linux' in platforms:
        kind = 'background' if (app, 'background', 'light') in records and (app, 'background', 'dark') in records else 'transparent'
        combined = resources.adaptive(records[app, kind, 'light'], records[app, kind, 'dark'])
        if combined is None:
            raise SystemExit('Linux adaptive export requires matching theme geometry')
        write_text(stage / 'linux' / 'app.svg', resources.serialize(resources.rounded(combined, radius)))
    if 'android' in platforms:
        cook_android(build, palette)


def main() -> None:
    global COMPOSE_SKILL_DIR, PROJECT_ROOT, RSVG
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path)
    parser.add_argument('--source', '--source-svg', dest='sources', action='append', type=Path)
    parser.add_argument('--source-map', type=Path)
    parser.add_argument('--layout', choices=('original', 'compact', 'spacious'))
    parser.add_argument('--theme', choices=('light', 'dark', 'adaptive'), help='Explicit single-file theme role; use source-map for groups')
    parser.add_argument('--inspect-theme', action='store_true')
    parser.add_argument('--base-only', action='store_true')
    parser.add_argument('--platforms', default='web,apple,windows,linux,android')
    parser.add_argument('--allow-padding', action='store_true', help='Only after explicit authorization for the proposed transform')
    parser.add_argument('--allow-colors', action='store_true', help='Only after explicit complementary-color authorization')
    parser.add_argument('--replace-existing', action='store_true', help='Take over exact output paths only after user authorization')
    args = parser.parse_args()
    if bool(args.sources) == bool(args.source_map):
        parser.error('Supply --source (repeatable) or --source-map, exclusively')
    if args.source_map and (args.layout or args.theme):
        parser.error('--layout/--theme apply to --source; declare source-map roles in JSON')
    config = resources.load_map(args.source_map) if args.source_map else {'sources': resources.entries_for_sources(args.sources, args.layout, args.theme)}
    collected_config = {'sources': config['sources']} if args.inspect_theme else config
    records, backgrounds, sources = resources.collect(collected_config, args.allow_padding, args.allow_colors)
    if args.inspect_theme:
        report = resources.inventory(records)
        report['proposed_derivations'] = {k: config[k] for k in ('derive_layouts', 'derive_themes') if k in config}
        if len(config['sources']) == 1:
            entry = config['sources'][0]
            report['source'] = entry['path']
            report['theme_inferred'] = entry.get('theme_inferred', False)
            report['theme_mode'] = 'dual' if entry['theme'] == 'adaptive' else 'single-' + entry['theme']
            report['palettes'] = {}
            for theme in resources.THEMES:
                key = entry['layout'], entry['kind'], theme
                if key in records:
                    bg = backgrounds.get((entry['layout'], theme))
                    colors = [e.get('fill') for e in records[key].iter() if resources.tag(e) in resources.SHAPES and e.get('fill') not in (bg, 'none')]
                    report['palettes'][theme] = {'background': bg, 'ink': colors[0] if colors else None}
                    if len(colors) > 1:
                        report['palettes'][theme]['alert'] = colors[1]
        report['source_roles'] = config['sources']
        report['sources'] = [str(p) for p in sorted(sources)]
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    if args.project_root is None or not args.project_root.expanduser().is_absolute():
        raise SystemExit('--project-root must be explicitly supplied as an absolute path')
    # Canonicalize user-selected target; publish rejects redirects inside its tree.
    raw_target = args.project_root.expanduser()
    if raw_target.is_symlink():
        raise SystemExit('Output target cannot be a symlink')
    target = raw_target.resolve()
    if target.exists() and not target.is_dir():
        raise SystemExit('Output target must be a directory')
    platforms = [] if args.base_only else [p.strip() for p in args.platforms.split(',') if p.strip()]
    if set(platforms) - {'web', 'apple', 'windows', 'linux', 'android'}:
        raise SystemExit('Unknown --platforms value')
    if platforms and any(not any(key[2] == theme for key in records) for theme in resources.THEMES):
        raise SystemExit('Do not generate or clean assets. Missing complementary theme requires explicit color authorization')
    if any(entry.get('theme_inferred') for entry in config['sources']):
        raise SystemExit('Confirm the advisory single-theme role with --theme light|dark or --source-map before organizing it; do not guess its semantic role')
    PROJECT_ROOT = target
    COMPOSE_SKILL_DIR = target / '.agents' / 'skills' / 'compose-app-icon'
    if platforms:
        platform_plan(records, backgrounds, config, platforms)
    validator = preflight_compose_skill() if 'apple' in platforms else None
    RSVG = require('rsvg-convert')
    if Image is None:
        raise SystemExit('Pillow is required for raster verification; inspection and select_logo.py remain available')
    if 'apple' in platforms:
        require('iconutil')
    with tempfile.TemporaryDirectory(prefix='app-logo-cook-') as temp:
        build = Path(temp) / 'build'
        stage = Path(temp) / 'stage'
        build.mkdir()
        stage.mkdir()
        try:
            PROJECT_ROOT = stage
            validate_base(stage, build, records)
            if platforms:
                build_platforms(stage, build, records, backgrounds, config, platforms, validator)
                validate_platform_files(stage, platforms)
            write_usage_readme(config, records, platforms)
        finally:
            PROJECT_ROOT = target
        preserve_in_place_sources(stage, target, sources, build)
        publish(stage, target, sources, args.replace_existing)
    print(f'Cooked validated resources into {target}')


if __name__ == '__main__':
    main()
