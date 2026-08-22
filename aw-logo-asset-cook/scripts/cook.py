#!/usr/bin/env python3
"""Cook the minimal platform icon set from the project's single root SVG."""

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


def discover_source() -> Path:
    candidates = sorted(path for path in PROJECT_ROOT.glob("*.svg") if path.is_file())
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise SystemExit("No SVG exists in the project root. Ask the user to add the canonical SVG.")
    names = ", ".join(path.name for path in candidates)
    raise SystemExit(f"Multiple root SVGs found: {names}. Ask the user which SVG is canonical.")


def svg_palette(source: Path) -> dict[str, dict[str, str]]:
    root = ET.parse(source).getroot()
    style = root.find(f"{{{SVG_NS}}}style")
    css = style.text if style is not None and style.text else ""
    light: dict[str, str] = {}
    for path in root.findall(f"{{{SVG_NS}}}path"):
        classes = set(path.attrib.get("class", "").split())
        fill = path.attrib.get("fill")
        if not fill:
            continue
        if "bg" in classes:
            light["background"] = fill
        elif "alert" in classes:
            light["alert"] = fill
        elif "ink" not in light:
            light["ink"] = fill

    patterns = {
        "ink": r"path\s*\{[^}]*fill:\s*(#[0-9A-Fa-f]{6})",
        "background": r"path\.bg\s*\{[^}]*fill:\s*(#[0-9A-Fa-f]{6})",
        "alert": r"path\.alert\s*\{[^}]*fill:\s*(#[0-9A-Fa-f]{6})",
    }
    dark = {}
    for role, pattern in patterns.items():
        match = re.search(pattern, css, flags=re.DOTALL)
        if match:
            dark[role] = match.group(1)

    for theme, palette in (("light", light), ("dark", dark)):
        missing = {"background", "ink", "alert"} - palette.keys()
        if missing:
            raise SystemExit(f"Canonical SVG is missing {theme} color roles: {', '.join(sorted(missing))}")
    return {"light": light, "dark": dark}


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


def srgb(hex_color: str) -> str:
    value = hex_color.lstrip("#")
    channels = [int(value[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    return "srgb:" + ",".join(f"{channel:.10f}".rstrip("0").rstrip(".") for channel in channels) + ",1"


def clean_outputs() -> None:
    for dirname in GENERATED_DIRS + LEGACY_DIRS:
        target = PROJECT_ROOT / dirname
        if target.is_dir():
            shutil.rmtree(target)
    for filename in LEGACY_FILES:
        target = PROJECT_ROOT / filename
        if target.is_file():
            target.unlink()


def cook_web(source: Path, light_png: Path) -> None:
    copy_asset(source, PROJECT_ROOT / "web" / "favicon.svg")
    save_ico(light_png, PROJECT_ROOT / "web" / "favicon.ico", [16, 32, 48])


def cook_apple(build: Path, palette: dict[str, dict[str, str]], validator: Path) -> None:
    root = PROJECT_ROOT / "iOS&macOS"
    package = root / "app" / "app.icon"
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
    render(build / "full-light.svg", root / "play-store-512.png", 512)


def main() -> None:
    global COMPOSE_SKILL_DIR, PROJECT_ROOT, RSVG
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        required=True,
        type=Path,
        help="Absolute path to the favicon-package project root",
    )
    args = parser.parse_args()
    project_root = args.project_root.expanduser()
    if not project_root.is_absolute():
        raise SystemExit("--project-root must be an absolute path")
    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise SystemExit(f"Project root does not exist or is not a directory: {project_root}")
    PROJECT_ROOT = project_root
    COMPOSE_SKILL_DIR = PROJECT_ROOT / ".agents" / "skills" / "compose-app-icon"
    validator = preflight_compose_skill()
    RSVG = require("rsvg-convert")
    source = discover_source()
    palette = svg_palette(source)
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
            build / "foreground-mono.svg",
            variant_svg(source, palette, "light", foreground=True, monochrome="#FFFFFF", canvas=1024),
        )
        write_text(
            build / "status-template.svg",
            variant_svg(source, palette, "light", foreground=True, monochrome="#000000"),
        )
        light_png = build / "full-light-1024.png"
        render(build / "full-light.svg", light_png, 1024)
        cook_web(source, light_png)
        cook_apple(build, palette, validator)
        cook_windows(build, light_png)
        cook_linux(source)
        cook_android(build, palette)

    print(f"Cooked minimal app assets from {source.name}")


if __name__ == "__main__":
    main()
