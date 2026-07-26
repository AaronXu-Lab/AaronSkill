#!/usr/bin/env python3
"""Fill 产品线 and 所属项目 dropdowns in the DingTalk daily report table."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import time


DEFAULT_PRODUCT_X = 828
DEFAULT_PROJECT_X = 940
DEFAULT_FIRST_ROW_Y = 302
DEFAULT_ROW_GAP = 50
DEFAULT_FIRST_MENU_ITEM_Y = 288
DEFAULT_MENU_ITEM_GAP = 36
SCRIPT_DIR = Path(__file__).resolve().parent


def osascript(*lines: str) -> None:
    args: list[str] = ["osascript"]
    for line in lines:
        args.extend(["-e", line])
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def ensure_dingtalk_frontmost() -> None:
    args = ["osascript", "-e", 'tell application "System Events" to get name of first process whose frontmost is true']
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    frontmost = result.stdout.strip()
    if result.returncode == 0 and frontmost == "DingTalk":
        return
    if result.returncode == 0 and frontmost in {"Codex", "Claude"} and os.environ.get("DINGTALK_ALLOW_ACTIVATE") == "1":
        subprocess.run(["osascript", "-e", 'tell application "DingTalk" to activate'], text=True, capture_output=True, check=False)
        time.sleep(0.4)
        result = subprocess.run(args, text=True, capture_output=True, check=False)
        if result.returncode == 0 and result.stdout.strip() == "DingTalk":
            return
    raise RuntimeError(f"DingTalk is not frontmost; frontmost app is {frontmost or 'unknown'}")


def click(x: int, y: int) -> None:
    ensure_dingtalk_frontmost()
    osascript(
        f'tell application "System Events" to click at {{{x}, {y}}}',
    )


def cg_click(x: int, y: int) -> None:
    ensure_dingtalk_frontmost()
    result = subprocess.run(
        ["python3", str(SCRIPT_DIR / "dingtalk_cg_click.py"), str(x), str(y)],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "DINGTALK_ALLOW_ACTIVATE": os.environ.get("DINGTALK_ALLOW_ACTIVATE", "1")},
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def click_point(x: int, y: int, driver: str, scale_x: float, scale_y: float) -> None:
    if driver == "cg":
        cg_click(round(x * scale_x), round(y * scale_y))
    else:
        click(x, y)


def select_dropdown(
    cell_x: int,
    cell_y: int,
    item_index: int,
    menu_x: int,
    menu_first_y: int,
    item_gap: int,
    delay: float,
    driver: str,
    scale_x: float,
    scale_y: float,
) -> None:
    click_point(cell_x, cell_y, driver, scale_x, scale_y)
    time.sleep(delay)
    click_point(menu_x, menu_first_y + (item_index - 1) * item_gap, driver, scale_x, scale_y)
    time.sleep(delay)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--product-x", type=int, default=DEFAULT_PRODUCT_X)
    parser.add_argument("--project-x", type=int, default=DEFAULT_PROJECT_X)
    parser.add_argument("--first-row-y", type=int, default=DEFAULT_FIRST_ROW_Y)
    parser.add_argument("--row-gap", type=int, default=DEFAULT_ROW_GAP)
    parser.add_argument("--menu-x", type=int, default=DEFAULT_PRODUCT_X)
    parser.add_argument("--first-menu-item-y", type=int, default=DEFAULT_FIRST_MENU_ITEM_Y)
    parser.add_argument("--menu-item-gap", type=int, default=DEFAULT_MENU_ITEM_GAP)
    parser.add_argument("--product-item", type=int, default=1, help="产品线 item index; default 1 means 其它.")
    parser.add_argument("--project-item", type=int, default=2, help="所属项目 item index; default 2 means 非交付投入.")
    parser.add_argument("--driver", choices=["applescript", "cg"], default="cg")
    parser.add_argument("--scale-x", type=float, default=2.0)
    parser.add_argument("--scale-y", type=float, default=2.0)
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for index in range(args.rows):
        y = args.first_row_y + index * args.row_gap
        print(f"row {index + 1}: product at {args.product_x},{y}; project at {args.project_x},{y}")
        if args.dry_run:
            continue
        select_dropdown(
            args.product_x,
            y,
            args.product_item,
            args.menu_x,
            args.first_menu_item_y,
            args.menu_item_gap,
            args.delay,
            args.driver,
            args.scale_x,
            args.scale_y,
        )
        select_dropdown(
            args.project_x,
            y,
            args.project_item,
            args.menu_x,
            args.first_menu_item_y,
            args.menu_item_gap,
            args.delay,
            args.driver,
            args.scale_x,
            args.scale_y,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
