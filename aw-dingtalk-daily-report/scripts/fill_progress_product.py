#!/usr/bin/env python3
"""Fill visible 进度 and 产品线 columns after horizontal table scroll."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_PROGRESS_X = 1336
DEFAULT_PRODUCT_X = 1492
DEFAULT_FIRST_ROW_Y = 554
DEFAULT_ROW_GAP = 93
DEFAULT_PRODUCT_MENU_X = 1492
DEFAULT_PRODUCT_MENU_FIRST_Y = 530


def osascript(*lines: str) -> str:
    args: list[str] = ["osascript"]
    for line in lines:
        args.extend(["-e", line])
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def ensure_dingtalk_frontmost() -> None:
    frontmost = osascript('tell application "System Events" to get name of first process whose frontmost is true')
    if frontmost == "DingTalk":
        return
    if frontmost in {"Codex", "Claude"} and os.environ.get("DINGTALK_ALLOW_ACTIVATE") == "1":
        subprocess.run(["osascript", "-e", 'tell application "DingTalk" to activate'], text=True, capture_output=True, check=False)
        time.sleep(0.4)
        frontmost = osascript('tell application "System Events" to get name of first process whose frontmost is true')
        if frontmost == "DingTalk":
            return
    raise RuntimeError(f"DingTalk is not frontmost; frontmost app is {frontmost or 'unknown'}")


def cg_click(x: int, y: int, scale_x: float, scale_y: float) -> None:
    ensure_dingtalk_frontmost()
    result = subprocess.run(
        ["python3", str(SCRIPT_DIR / "dingtalk_cg_click.py"), str(round(x * scale_x)), str(round(y * scale_y))],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "DINGTALK_ALLOW_ACTIVATE": os.environ.get("DINGTALK_ALLOW_ACTIVATE", "1")},
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def replace_text(text: str) -> None:
    ensure_dingtalk_frontmost()
    subprocess.run(["pbcopy"], input=text, text=True, check=True)
    osascript(
        'tell application "System Events" to keystroke "a" using command down',
        'delay 0.05',
        'tell application "System Events" to keystroke "v" using command down',
    )


def load_rows(raw: str) -> list[dict[str, Any]]:
    rows = json.loads(raw)
    if not isinstance(rows, list) or not rows:
        raise ValueError("--rows must be a non-empty JSON list")
    for row in rows:
        if not isinstance(row, dict) or "progress" not in row:
            raise ValueError('Each row must be an object with "progress"')
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", required=True, help='JSON list with "progress" for each visible row.')
    parser.add_argument("--progress-x", type=int, default=DEFAULT_PROGRESS_X)
    parser.add_argument("--product-x", type=int, default=DEFAULT_PRODUCT_X)
    parser.add_argument("--first-row-y", type=int, default=DEFAULT_FIRST_ROW_Y)
    parser.add_argument("--row-gap", type=int, default=DEFAULT_ROW_GAP)
    parser.add_argument("--product-menu-x", type=int, default=DEFAULT_PRODUCT_MENU_X)
    parser.add_argument("--product-menu-first-y", type=int, default=DEFAULT_PRODUCT_MENU_FIRST_Y)
    parser.add_argument("--product-item", type=int, default=1, help="产品线 dropdown index. Default 1 is 其他.")
    parser.add_argument("--menu-item-gap", type=int, default=36)
    parser.add_argument("--scale-x", type=float, default=1.0)
    parser.add_argument("--scale-y", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--skip-product", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = load_rows(args.rows)
    for index, row in enumerate(rows):
        y = args.first_row_y + index * args.row_gap
        print(f"row {index + 1}: progress at {args.progress_x},{y}; product at {args.product_x},{y}")
        if args.dry_run:
            continue
        cg_click(args.progress_x, y, args.scale_x, args.scale_y)
        time.sleep(args.delay)
        replace_text(str(row["progress"]))
        time.sleep(args.delay)
        if args.skip_product:
            continue
        cg_click(args.product_x, y, args.scale_x, args.scale_y)
        time.sleep(args.delay)
        cg_click(args.product_menu_x, args.product_menu_first_y + (args.product_item - 1) * args.menu_item_gap, args.scale_x, args.scale_y)
        time.sleep(args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
