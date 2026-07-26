#!/usr/bin/env python3
"""Fill visible 所属项目 dropdowns after horizontal table scroll."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import time


SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_PROJECT_X = 705
DEFAULT_FIRST_ROW_Y = 292
DEFAULT_ROW_GAP = 55
DEFAULT_MENU_X = 684
DEFAULT_MENU_FIRST_Y = 263
DEFAULT_MENU_ITEM_GAP = 36


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--project-x", type=int, default=DEFAULT_PROJECT_X)
    parser.add_argument("--first-row-y", type=int, default=DEFAULT_FIRST_ROW_Y)
    parser.add_argument("--row-gap", type=int, default=DEFAULT_ROW_GAP)
    parser.add_argument("--menu-x", type=int, default=DEFAULT_MENU_X)
    parser.add_argument("--menu-first-y", type=int, default=DEFAULT_MENU_FIRST_Y)
    parser.add_argument("--menu-item-gap", type=int, default=DEFAULT_MENU_ITEM_GAP)
    parser.add_argument("--project-item", type=int, default=2, help="所属项目 dropdown index. Default 2 is 非交付投入.")
    parser.add_argument("--scale-x", type=float, default=2.0)
    parser.add_argument("--scale-y", type=float, default=2.0)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for index in range(args.rows):
        y = args.first_row_y + index * args.row_gap
        print(f"row {index + 1}: project at {args.project_x},{y}")
        if args.dry_run:
            continue
        cg_click(args.project_x, y, args.scale_x, args.scale_y)
        time.sleep(args.delay)
        cg_click(args.menu_x, args.menu_first_y + (args.project_item - 1) * args.menu_item_gap, args.scale_x, args.scale_y)
        time.sleep(args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
