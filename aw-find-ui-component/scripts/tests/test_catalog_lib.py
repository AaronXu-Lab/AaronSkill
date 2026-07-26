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
    parse_markdown_index,
    parse_markdown_link_prefix,
    parse_registry_sitemap,
    parse_shadcn_cli,
    refresh_catalogs,
    search_catalog,
)


class CatalogParsingTests(unittest.TestCase):
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
        self.assertTrue(items[0]["port_eligible"])

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
            "id": "exabase",
            "name": "exaBase",
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
        self.assertEqual(items[0]["license"], "MIT public only")


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
                        "schema_version": 1,
                        "sources": [
                            {
                                "id": "example",
                                "name": "Example",
                                "kind": "markdown_index",
                                "catalog_url": "https://example.test/llms.txt",
                                "sections": ["Components"],
                                "foundation": "base-ui",
                                "variant": "base",
                                "base_ui_evidence": "verified",
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
            self.assertEqual(entry["items"], [cached_item])
            self.assertIn("offline", entry["error"])


class CatalogSearchTests(unittest.TestCase):
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
