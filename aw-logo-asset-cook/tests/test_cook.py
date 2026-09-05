#!/usr/bin/env python3
"""Focused tests for explicit source resolution and SVG theme inspection."""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cook.py"
SPEC = importlib.util.spec_from_file_location("aw_logo_asset_cook", SCRIPT)
assert SPEC and SPEC.loader
COOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COOK)


def svg(background: str, ink: str, alert: str, media: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <style>{media}</style>
  <path class="bg" fill="{background}" d="M0 0h32v32H0z"/>
  <path class="ink" fill="{ink}" d="M4 4h24v24H4z"/>
  <path class="alert" fill="{alert}" d="M12 12h8v8h-8z"/>
</svg>
"""


class ThemeInspectionTests(unittest.TestCase):
    def inspect(self, content: str) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "logo.svg"
            source.write_text(content, encoding="utf-8")
            return COOK.inspect_svg_palette(source)

    def test_detects_existing_light_and_dark_themes(self) -> None:
        media = """@media (prefers-color-scheme: dark) {
          path { fill: #F4F4F4; }
          path.bg { fill: #111111; }
          path.alert { fill: #FF7755; }
        }"""
        result = self.inspect(svg("#FFFFFF", "#111111", "#CC2200", media))
        self.assertEqual(result["theme_mode"], "dual")
        self.assertEqual(result["palettes"]["light"]["background"], "#FFFFFF")
        self.assertEqual(result["palettes"]["dark"]["background"], "#111111")

    def test_detects_single_light_theme(self) -> None:
        result = self.inspect(svg("#FFFFFF", "#111111", "#CC2200"))
        self.assertEqual(result["theme_mode"], "single-light")

    def test_detects_single_dark_theme(self) -> None:
        result = self.inspect(svg("#101010", "#F4F4F4", "#FF7755"))
        self.assertEqual(result["theme_mode"], "single-dark")

    def test_cooking_guard_rejects_single_theme(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "logo.svg"
            source.write_text(svg("#FFFFFF", "#111111", "#CC2200"), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "Do not generate or clean assets"):
                COOK.svg_palette(source)

    def test_single_theme_stops_before_dependency_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp).resolve()
            source = project / "logo.svg"
            source.write_text(svg("#FFFFFF", "#111111", "#CC2200"), encoding="utf-8")
            argv = [
                "cook.py",
                "--source-svg",
                str(source),
                "--project-root",
                str(project),
            ]
            with (
                mock.patch("sys.argv", argv),
                mock.patch.object(COOK, "preflight_compose_skill") as preflight,
                mock.patch.object(COOK, "clean_outputs") as clean,
            ):
                with self.assertRaisesRegex(SystemExit, "Do not generate or clean assets"):
                    COOK.main()
                preflight.assert_not_called()
                clean.assert_not_called()


class SourceResolutionTests(unittest.TestCase):
    def test_accepts_explicit_svg_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp).resolve() / "logo.svg"
            source.write_text(svg("#FFFFFF", "#111111", "#CC2200"), encoding="utf-8")
            self.assertEqual(COOK.resolve_source(source), source)

    def test_accepts_only_root_svg_in_explicit_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp).resolve()
            source = directory / "icon.svg"
            source.write_text(svg("#FFFFFF", "#111111", "#CC2200"), encoding="utf-8")
            nested = directory / "nested"
            nested.mkdir()
            (nested / "ignored.svg").write_text(svg("#FFFFFF", "#111111", "#CC2200"), encoding="utf-8")
            self.assertEqual(COOK.resolve_source(directory), source)

    def test_rejects_directory_without_root_svg(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(SystemExit, "No SVG exists at the root"):
                COOK.resolve_source(Path(temp).resolve())

    def test_rejects_ambiguous_root_svgs_and_lists_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp).resolve()
            for name in ("a.svg", "b.svg"):
                (directory / name).write_text(svg("#FFFFFF", "#111111", "#CC2200"), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "a\\.svg[\\s\\S]*b\\.svg"):
                COOK.resolve_source(directory)


class WebAssetTests(unittest.TestCase):
    def test_full_bleed_svg_replaces_source_background_with_square_fill(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "logo.svg"
            source.write_text(svg("#FFF9EF", "#002138", "#CB0234"), encoding="utf-8")
            palette = {
                "light": {"background": "#FFF9EF", "ink": "#002138", "alert": "#CB0234"},
                "dark": {"background": "#140C00", "ink": "#F3F9FF", "alert": "#FFC53D"},
            }

            result = COOK.variant_svg(source, palette, "light", full_bleed=True)
            root = COOK.ET.fromstring(result)
            children = list(root)

            self.assertEqual(children[0].tag, f"{{{COOK.SVG_NS}}}rect")
            self.assertEqual(children[0].attrib, {"width": "32", "height": "32", "fill": "#FFF9EF"})
            self.assertFalse(any("bg" in child.attrib.get("class", "").split() for child in children))

    def test_maskable_icon_has_opaque_background_and_padded_foreground(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "foreground.png"
            output = root / "icon-maskable-512.png"
            foreground = COOK.Image.new("RGBA", (100, 100), (0, 0, 0, 0))
            foreground.paste((0, 33, 56, 255), (0, 0, 100, 100))
            foreground.save(source)

            COOK.save_maskable_icon(source, output, 512, "#FFF9EF")

            with COOK.Image.open(output).convert("RGBA") as result:
                self.assertEqual(result.getchannel("A").getextrema(), (255, 255))
                self.assertEqual(result.getpixel((0, 0)), (255, 249, 239, 255))
                self.assertEqual(result.getpixel((256, 256)), (0, 33, 56, 255))

    def test_pwa_manifest_references_all_generated_icons_relatively(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            COOK.write_pwa_manifest(root)
            manifest = COOK.json.loads((root / "manifest.webmanifest").read_text(encoding="utf-8"))

            self.assertEqual(
                [icon["src"] for icon in manifest["icons"]],
                ["icon-192.png", "icon-512.png", "icon-maskable-512.png"],
            )
            self.assertEqual(manifest["icons"][2]["purpose"], "maskable")


class AndroidAssetTests(unittest.TestCase):
    def test_play_store_png_keeps_fully_opaque_alpha_channel(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "play-store-512.png"
            COOK.Image.new("RGB", (512, 512), (255, 249, 239)).save(output)

            COOK.force_rgba_png(output)

            with COOK.Image.open(output) as result:
                self.assertEqual(result.mode, "RGBA")
                self.assertEqual(result.getchannel("A").getextrema(), (255, 255))
            self.assertEqual(output.read_bytes()[25], 6)


class MacOSLegacyTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("iconutil") and shutil.which("rsvg-convert"), "macOS icon tools required")
    def test_icns_roundtrip_preserves_sizes_colors_and_transparency(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build = root / "build"
            build.mkdir()
            (build / "full-light.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
                '<rect x="4" y="4" width="24" height="24" fill="#CC2200"/></svg>'
            )
            with mock.patch.object(COOK, "PROJECT_ROOT", root), mock.patch.object(
                COOK, "RSVG", shutil.which("rsvg-convert"), create=True
            ):
                COOK.cook_macos_legacy(build)
            output = root / "iOS&macOS" / "app.icns"
            self.assertEqual(output.read_bytes()[:4], b"icns")
            for points in (16, 32, 128, 256, 512):
                for scale in (1, 2):
                    suffix = "@2x" if scale == 2 else ""
                    with COOK.Image.open(build / "roundtrip.iconset" / f"icon_{points}x{points}{suffix}.png") as image:
                        self.assertEqual(image.size, (points * scale, points * scale))
                        rgba = image.convert("RGBA")
                        self.assertEqual(rgba.getpixel((0, 0))[3], 0)
                        self.assertEqual(rgba.getpixel((points * scale // 2, points * scale // 2)), (204, 34, 0, 255))
            self.assertEqual([p.name for p in output.parent.iterdir()], ["app.icns"])


class UsageReadmeTests(unittest.TestCase):
    def test_readme_maps_generated_paths_without_brand_specific_names(self) -> None:
        expected_paths = (
            "web/favicon.svg",
            "web/apple-touch-icon.png",
            "web/pwa/manifest.webmanifest",
            "iOS&macOS/app.icon",
            "iOS&macOS/app.icns",
            "iOS&macOS/menu-bar/appTemplate.svg",
            "windows/app.ico",
            "windows/tray-light.ico",
            "windows/tray-dark.ico",
            "linux/app.svg",
            "android/res/",
            "android/play-store-512.png",
        )
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            source = project / "logo.svg"
            with mock.patch.object(COOK, "PROJECT_ROOT", project):
                COOK.write_usage_readme(source)
            content = (project / "README.md").read_text(encoding="utf-8")

            for path in expected_paths:
                self.assertIn(path, content)
            self.assertNotIn("AXO", content.upper())


if __name__ == "__main__":
    unittest.main()
