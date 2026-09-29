from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from catalog_lib import (  # noqa: E402
    load_alias_terms,
    parse_github_tree_paths,
    parse_github_tree_sitemap,
    parse_lobe_ui_index,
    parse_markdown_index,
    parse_markdown_link_prefix,
    parse_registry_sitemap,
    parse_shadcn_cli,
    parse_shadcn_registry_variants,
    refresh_catalogs,
    search_catalog,
)


class CatalogParsingTests(unittest.TestCase):
    def test_lobe_ui_index_joins_grouped_docs_to_exact_source(self) -> None:
        source = {
            "id": "lobe-ui", "name": "Lobe UI",
            "source_template": "https://github.com/lobehub/lobe-ui/blob/master/{path}",
            "type": {"foundation": "mixed", "styling": "antd-style"},
            "license": "MIT",
        }
        index = "\n".join([
            "- [Button](https://ui.lobehub.com/skills/components/button.md): Button. Docs: https://ui.lobehub.com/components/button",
            "- [ChatInputArea](https://ui.lobehub.com/skills/components/chat/chat-input-area.md): Chat input.",
            "- [ChatInputArea](https://ui.lobehub.com/skills/components/mobile/chat-input-area.md): Mobile chat input.",
            "- [Missing](https://ui.lobehub.com/skills/components/missing.md): Absent source.",
        ])
        tree = json.dumps({"truncated": False, "tree": [
            {"type": "blob", "path": path} for path in [
                "src/Button/index.mdx", "src/Button/index.ts",
                "src/chat/ChatInputArea/index.mdx", "src/chat/ChatInputArea/index.ts",
                "src/mobile/ChatInputArea/index.mdx", "src/mobile/ChatInputArea/index.ts",
            ]
        ]})
        items = parse_lobe_ui_index(source, index, tree)
        self.assertEqual(len(items), 3)
        by_slug = {item["slug"]: item for item in items}
        self.assertEqual(by_slug["chat/chat-input-area"]["preview_url"], "https://ui.lobehub.com/components/chat/chat-input-area")
        self.assertTrue(by_slug["chat/chat-input-area"]["source_url"].endswith("/src/chat/ChatInputArea/index.ts"))
        self.assertEqual(by_slug["mobile/chat-input-area"]["category"], "mobile")
        self.assertEqual(items[0]["foundation"], "unverified")
        self.assertFalse(items[0]["port_eligible"])

    def test_shadcn_cli_parser_keeps_only_ui_items_with_base_pages(self) -> None:
        source = {
            "id": "shadcn",
            "name": "shadcn",
            "preview_template": "https://example.test/base/{slug}",
            "source_template": "https://example.test/source/{slug}.tsx",
            "foundation": "base-ui",
            "variant": "base",
            "license": "MIT",
            "base_ui_evidence": "verified",
        }
        registry = json.dumps(
            {
                "items": [
                    {"name": "message", "type": "registry:ui"},
                    {"name": "radix-only", "type": "registry:ui"},
                    {"name": "message-demo", "type": "registry:example"},
                ]
            }
        )
        items = parse_shadcn_cli(
            source,
            registry,
            validator=lambda url: url.endswith("/base/message"),
        )
        self.assertEqual([item["slug"] for item in items], ["message"])
        self.assertEqual(items[0]["source_url"], "https://example.test/source/message.tsx")

    def test_markdown_parser_keeps_only_sections_and_verified_base_previews(self) -> None:
        source = {
            "id": "example",
            "name": "Example",
            "sections": ["Components"],
            "preview_template": "https://example.test/base/{slug}",
            "verify_preview": True,
            "foundation": "base-ui",
            "variant": "base",
            "license": "MIT",
            "base_ui_evidence": "verified",
        }
        markdown = """
## Overview
- [Ignored](https://example.test/ignored): Not a component.
## Components
- [Message](https://example.test/message): Conversation row.
- [Radix Only](https://example.test/radix-only): Wrong variant.
## Hooks
- [useThing](https://example.test/use-thing): Hook.
"""
        items = parse_markdown_index(
            source,
            markdown,
            validator=lambda url: url.endswith("/base/message"),
        )
        self.assertEqual([item["slug"] for item in items], ["message"])
        self.assertFalse(items[0]["port_eligible"])
        self.assertEqual(items[0]["verification_status"], "unverified")

    def test_markdown_parser_maps_official_component_docs_to_source(self) -> None:
        source = {
            "id": "base-ui-official",
            "name": "Base UI",
            "sections": ["Components"],
            "strip_preview_suffix": ".md",
            "source_template": "https://github.com/mui/base-ui/tree/master/packages/react/src/{slug}",
            "verify_preview": True,
            "base_ui_evidence": "official docs and source",
        }
        markdown = """## Components
- [Accordion](https://base-ui.com/react/components/accordion.md): Panels.
## Utilities
- [useRender](https://base-ui.com/react/utils/use-render.md): Utility.
"""
        items = parse_markdown_index(
            source,
            markdown,
            validator=lambda url: url == "https://base-ui.com/react/components/accordion",
        )
        self.assertEqual([item["slug"] for item in items], ["accordion"])
        self.assertEqual(
            items[0]["preview_url"], "https://base-ui.com/react/components/accordion"
        )
        self.assertEqual(
            items[0]["source_url"],
            "https://github.com/mui/base-ui/tree/master/packages/react/src/accordion",
        )

    def test_registry_parser_intersects_base_sitemap_and_component_types(self) -> None:
        source = {
            "id": "dice",
            "name": "Dice",
            "sitemap_prefix": "https://example.test/docs/components/base/",
            "preview_template": "https://example.test/docs/components/base/{slug}",
            "source_template": "https://example.test/r/base/{slug}.json",
            "forbidden_dependencies": ["radix-ui", "@radix-ui/"],
            "foundation": "base-ui",
            "variant": "base",
            "license": "MIT",
            "base_ui_evidence": "verified",
        }
        registry = json.dumps(
            {
                "items": [
                    {"name": "status", "type": "registry:ui"},
                    {
                        "name": "slot-based",
                        "type": "registry:ui",
                        "dependencies": ["radix-ui"],
                    },
                    {"name": "demo", "type": "registry:example"},
                    {"name": "radix-only", "type": "registry:ui"},
                ]
            }
        )
        sitemap = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.test/docs/components/base/status</loc></url>
  <url><loc>https://example.test/docs/components/base/slot-based</loc></url>
  <url><loc>https://example.test/docs/components/radix/radix-only</loc></url>
</urlset>"""
        items = parse_registry_sitemap(source, registry, sitemap)
        self.assertEqual([item["slug"] for item in items], ["status"])

    def test_nested_markdown_parser_keeps_only_component_links(self) -> None:
        source = {
            "id": "nested-docs",
            "name": "Nested Docs",
            "base_url": "https://example.test/design/",
            "link_prefix": "/docs/components/",
            "preview_template": "https://example.test/design/docs/components/{slug}/",
            "source_template": "https://example.test/design/registry/{slug}.json",
            "foundation": "base-ui",
            "variant": "base",
            "license": "mixed",
            "base_ui_evidence": "verify exact source",
        }
        markdown = """
- Getting Started
  - [Installation](/docs/getting-started/installation): Install.
- Components
  - [Breadcrumb](/docs/components/breadcrumb): Navigation hierarchy.
  - [Data Table](/docs/components/data-table): Tabular data.
"""
        items = parse_markdown_link_prefix(source, markdown)
        self.assertEqual(
            [item["slug"] for item in items], ["breadcrumb", "data-table"]
        )
        self.assertEqual(
            items[0]["source_url"],
            "https://example.test/design/registry/breadcrumb.json",
        )

    def test_github_tree_parser_keeps_direct_base_component_metadata(self) -> None:
        source = {
            "id": "reui",
            "name": "ReUI",
            "path_prefix": "meta/base/",
            "path_suffix": ".json",
            "preview_template": "https://example.test/components/{slug}",
            "source_template": "https://github.test/base/{slug}",
            "foundation": "base-ui",
            "variant": "base",
            "license": "MIT public only",
            "base_ui_evidence": "public base path",
        }
        tree = json.dumps(
            {
                "tree": [
                    {"path": "meta/base/breadcrumb.json", "type": "blob"},
                    {"path": "meta/base/nested/ignored.json", "type": "blob"},
                    {"path": "meta/radix/dialog.json", "type": "blob"},
                    {"path": "meta/base/button.json", "type": "tree"},
                ]
            }
        )
        items = parse_github_tree_paths(source, tree)
        self.assertEqual([item["slug"] for item in items], ["breadcrumb"])
        self.assertEqual(items[0]["license"], "unverified")
        self.assertEqual(items[0]["source_license_hint"], "MIT public only")

    def test_astryx_sitemap_keeps_components_and_maps_nested_source(self) -> None:
        source = {
            "id": "astryx",
            "name": "Astryx",
            "type": {"foundation": "custom", "styling": "stylex"},
            "sitemap_prefix": "https://astryx.atmeta.com/components/",
            "path_prefix": "packages/core/src/",
            "source_template": "https://github.com/facebook/astryx/blob/main/{path}",
            "license": "MIT",
        }
        tree = json.dumps({"tree": [
            {"path": "packages/core/src/Button/Button.tsx", "type": "blob"},
            {"path": "packages/core/src/Avatar/AvatarStatusDot.tsx", "type": "blob"},
        ]})
        sitemap = """<urlset><url><loc>https://astryx.atmeta.com/components/Button</loc></url>
<url><loc>https://astryx.atmeta.com/components/AvatarStatusDot</loc></url>
<url><loc>https://astryx.atmeta.com/components/useButton</loc></url></urlset>"""
        items = parse_github_tree_sitemap(source, tree, sitemap)
        self.assertEqual([item["slug"] for item in items], ["AvatarStatusDot", "Button"])
        self.assertTrue(items[0]["source_url"].endswith("/Avatar/AvatarStatusDot.tsx"))
        self.assertEqual(items[0]["foundation_hint"], "custom")
        self.assertEqual(items[0]["styling_hint"], "stylex")
        self.assertEqual(items[0]["foundation"], "unverified")
        self.assertEqual(items[0]["license"], "unverified")

    def test_astryx_truncated_tree_is_not_treated_as_complete(self) -> None:
        source = {"path_prefix": "packages/core/src/", "sitemap_prefix": "https://astryx.atmeta.com/components/"}
        with self.assertRaisesRegex(ValueError, "truncated"):
            parse_github_tree_sitemap(source, '{"truncated":true,"tree":[]}', "<urlset/>")

    def test_registry_variant_parser_keeps_base_radix_and_native_items(self) -> None:
        source = {
            "id": "fluid",
            "name": "Fluid",
            "preview_template": "https://example.test/docs/{slug}",
            "source_template": "https://example.test/r/{registry_slug}.json",
            "preferred_suffix": "-base",
            "preferred_title_suffix": " (Base UI)",
            "forbidden_dependencies": ["@radix-ui/"],
            "verify_preview": True,
            "foundation": "base-ui-or-native",
            "variant": "base-or-native",
            "license": "MIT",
            "base_ui_evidence": "verified",
        }
        registry = json.dumps(
            {
                "items": [
                    {
                        "name": "dialog",
                        "title": "Dialog",
                        "type": "registry:ui",
                        "dependencies": ["@radix-ui/react-dialog"],
                    },
                    {
                        "name": "dialog-base",
                        "title": "Dialog (Base UI)",
                        "type": "registry:ui",
                        "dependencies": ["@base-ui/react"],
                    },
                    {
                        "name": "badge",
                        "title": "Badge",
                        "type": "registry:ui",
                        "dependencies": ["class-variance-authority"],
                    },
                    {
                        "name": "radix-only",
                        "title": "Radix Only",
                        "type": "registry:ui",
                        "dependencies": ["@radix-ui/react-popover"],
                    },
                    {
                        "name": "utils",
                        "title": "Utilities",
                        "type": "registry:lib",
                    },
                ]
            }
        )
        items = parse_shadcn_registry_variants(
            source,
            registry,
            validator=lambda url: not url.endswith("/missing"),
        )
        self.assertEqual([item["slug"] for item in items], ["badge", "dialog", "dialog", "radix-only"])
        dialog = next(item for item in items if item["registry_slug"] == "dialog-base")
        self.assertEqual(dialog["name"], "Dialog")
        self.assertEqual(dialog["registry_slug"], "dialog-base")
        self.assertEqual(dialog["foundation_hint"], "base-ui")
        radix = next(item for item in items if item["registry_slug"] == "dialog")
        self.assertEqual(radix["foundation_hint"], "radix-ui")
        self.assertEqual(
            dialog["source_url"], "https://example.test/r/dialog-base.json"
        )

    def test_registry_parser_keeps_distinct_items_and_preview_overrides(self) -> None:
        source = {
            "id": "basecn",
            "name": "basecn",
            "preview_template": "https://example.test/docs/{slug}",
            "preview_overrides": {
                "form": "https://example.test/docs/form-with-react-hook-form"
            },
            "source_template": "https://example.test/r/{registry_slug}.json",
            "preferred_suffix": "",
            "verify_preview": True,
            "base_ui_evidence": "verify exact item",
        }
        registry = json.dumps(
            {
                "items": [
                    {"name": "form", "type": "registry:ui"},
                    {"name": "drawer", "type": "registry:ui"},
                    {"name": "drawer-base", "type": "registry:ui"},
                ]
            }
        )
        items = parse_shadcn_registry_variants(
            source,
            registry,
            validator=lambda url: url != "https://example.test/docs/form",
        )
        self.assertEqual([item["slug"] for item in items], ["drawer", "drawer-base", "form"])
        form = next(item for item in items if item["slug"] == "form")
        self.assertEqual(
            form["preview_url"], "https://example.test/docs/form-with-react-hook-form"
        )
        self.assertEqual(form["source_url"], "https://example.test/r/form.json")
        self.assertEqual(form["foundation"], "unverified")
        self.assertEqual(form["variant"], "unverified")
        self.assertEqual(form["license"], "unverified")


class CatalogRefreshTests(unittest.TestCase):
    def test_failed_refresh_preserves_cache_as_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sources_path = root / "sources.json"
            catalog_path = root / "catalog.json"
            catalogs_dir = root / "catalogs"
            sources_path.write_text(
                json.dumps(
                    {
                        "schema_version": 3,
                        "sources": [
                            {
                                "id": "example",
                                "name": "Example",
                                "description": "Example component library.",
                                "type": {"foundation": "base-ui", "styling": "unverified"},
                                "config": {
                                    "kind": "markdown_index",
                                    "catalog_url": "https://example.test/llms.txt",
                                    "sections": ["Components"],
                                    "base_ui_evidence": "verified",
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            cached_item = {
                "source_id": "example",
                "library": "Example",
                "name": "Button",
                "slug": "button",
                "description": "",
                "preview_url": "https://example.test/button",
                "source_url": None,
                "foundation": "base-ui",
                "variant": "base",
                "dependencies": [],
                "license": "MIT",
                "base_ui_evidence": "verified",
                "port_eligible": True,
            }
            catalog_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "generated_at": "earlier",
                        "sources": {
                            "example": {
                                "id": "example",
                                "name": "Example",
                                "status": "fresh",
                                "last_success_at": "earlier",
                                "items": [cached_item],
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            def failing_fetcher(*_args, **_kwargs):
                raise OSError("offline")

            catalog = refresh_catalogs(
                sources_path,
                catalog_path,
                catalogs_dir,
                fetcher=failing_fetcher,
            )
            entry = catalog["sources"]["example"]
            self.assertEqual(entry["status"], "stale")
            self.assertEqual(entry["description"], "Example component library.")
            self.assertEqual(entry["items"][0]["name"], cached_item["name"])
            self.assertEqual(entry["items"][0]["foundation_hint"], "base-ui")
            self.assertEqual(entry["items"][0]["foundation"], "unverified")
            self.assertFalse(entry["items"][0]["port_eligible"])
            self.assertIn("offline", entry["error"])

    def test_nested_source_config_refreshes_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sources_path = root / "sources.json"
            catalog_path = root / "catalog.json"
            catalogs_dir = root / "catalogs"
            sources_path.write_text(
                json.dumps(
                    {
                        "schema_version": 3,
                        "sources": [
                            {
                                "id": "example",
                                "name": "Example",
                                "description": "Example component library.",
                                "type": {"foundation": "base-ui", "styling": "unverified"},
                                "config": {
                                    "kind": "markdown_index",
                                    "catalog_url": "https://example.test/llms.txt",
                                    "sections": ["Components"],
                                    "source_template": "https://example.test/r/{slug}.json",
                                    "base_ui_evidence": "verify exact item",
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            def fetcher(*_args, **_kwargs):
                return "## Components\n- [Button](https://example.test/button): Action.\n", {}

            catalog = refresh_catalogs(
                sources_path,
                catalog_path,
                catalogs_dir,
                fetcher=fetcher,
            )
            entry = catalog["sources"]["example"]
            self.assertEqual(entry["status"], "fresh")
            self.assertEqual(entry["description"], "Example component library.")
            self.assertEqual([item["slug"] for item in entry["items"]], ["button"])
            self.assertEqual(
                entry["items"][0]["source_url"],
                "https://example.test/r/button.json",
            )


class CatalogSearchTests(unittest.TestCase):
    def test_equal_lexical_matches_show_base_first_without_hiding_other_foundations(self) -> None:
        catalog = {"sources": {"one": {
            "id": "one", "name": "One", "status": "fresh",
            "items": [
                {"name": "Dialog", "slug": "dialog", "foundation_hint": "radix-ui"},
                {"name": "Dialog", "slug": "dialog", "foundation_hint": "base-ui"},
            ],
        }}}
        result = search_catalog(catalog, "dialog", [])
        hints = [item["foundation_hint"] for item in result["sources"][0]["matches"]]
        self.assertEqual(hints, ["base-ui", "radix-ui"])

    def test_alias_search_and_explicit_no_match_per_source(self) -> None:
        catalog = {
            "generated_at": "now",
            "sources": {
                "one": {
                    "id": "one",
                    "name": "One",
                    "status": "fresh",
                    "last_success_at": "now",
                    "items": [
                        {
                            "source_id": "one",
                            "library": "One",
                            "name": "Message",
                            "slug": "message",
                            "description": "Conversation row",
                            "preview_url": "https://example.test/message",
                            "source_url": None,
                            "base_ui_evidence": "verified",
                        }
                    ],
                },
                "two": {
                    "id": "two",
                    "name": "Two",
                    "status": "fresh",
                    "last_success_at": "now",
                    "items": [],
                },
            },
        }
        result = search_catalog(catalog, "chat bubble", ["chat bubble", "message"])
        self.assertEqual(result["sources"][0]["matches"][0]["match"], "Equivalent")
        self.assertEqual(result["sources"][1]["matches"], [])

    def test_single_generic_word_in_description_is_not_a_match(self) -> None:
        catalog = {
            "sources": {
                "one": {
                    "id": "one",
                    "name": "One",
                    "status": "fresh",
                    "items": [
                        {
                            "name": "Toast",
                            "slug": "toast",
                            "description": "A temporary notification message.",
                        }
                    ],
                }
            }
        }
        result = search_catalog(catalog, "message", ["message", "chat message"])
        self.assertEqual(result["sources"][0]["matches"], [])

    def test_alias_file_expands_canonical_term(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "aliases.md"
            path.write_text(
                "| Canonical term | Common aliases |\n|---|---|\n| message | chat bubble, conversation row |\n",
                encoding="utf-8",
            )
            terms = load_alias_terms(path, "chat bubble")
            self.assertIn("message", terms)


if __name__ == "__main__":
    unittest.main()
