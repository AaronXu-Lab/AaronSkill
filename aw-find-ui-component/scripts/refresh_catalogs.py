#!/usr/bin/env python3
"""Refresh curated Base UI catalogs with stale-cache fallback."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from catalog_lib import refresh_catalogs


SKILL_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", help="Refresh only this source id")
    parser.add_argument("--force", action="store_true", help="Ignore conditional HTTP cache metadata")
    parser.add_argument("--json", action="store_true", help="Print machine-readable status")
    args = parser.parse_args()

    catalog = refresh_catalogs(
        SKILL_DIR / "references" / "sources.json",
        SKILL_DIR / "references" / "catalog.json",
        SKILL_DIR / "references" / "catalogs",
        selected_sources=set(args.source) if args.source else None,
        force=args.force,
    )
    statuses = [
        {
            "id": entry.get("id"),
            "name": entry.get("name"),
            "status": entry.get("status"),
            "count": len(entry.get("items", [])),
            "last_checked_at": entry.get("last_checked_at"),
            "last_success_at": entry.get("last_success_at"),
            "error": entry.get("error"),
        }
        for entry in catalog.get("sources", {}).values()
    ]
    if args.json:
        print(json.dumps({"sources": statuses}, indent=2, ensure_ascii=False))
    else:
        for status in statuses:
            print(
                f"{status['id']}: {status['status']} ({status['count']} components)"
                + (f" — {status['error']}" if status["error"] else "")
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
