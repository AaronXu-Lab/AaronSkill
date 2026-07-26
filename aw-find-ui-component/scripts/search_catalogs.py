#!/usr/bin/env python3
"""Search every curated library and preserve explicit no-match results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from catalog_lib import load_alias_terms, read_json, search_as_markdown, search_catalog


SKILL_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--alias", action="append", default=[])
    parser.add_argument("--limit-per-source", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    aliases = load_alias_terms(
        SKILL_DIR / "references" / "component-aliases.md", args.query
    )
    aliases.extend(args.alias)
    aliases = list(dict.fromkeys(alias for alias in aliases if alias.strip()))
    catalog = read_json(SKILL_DIR / "references" / "catalog.json", {})
    result = search_catalog(catalog, args.query, aliases, args.limit_per_source)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(search_as_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
