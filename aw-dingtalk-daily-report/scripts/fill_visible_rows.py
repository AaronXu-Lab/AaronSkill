#!/usr/bin/env python3
"""Fill visible DingTalk daily report row date and work-content cells."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


DEFAULT_DATE_X = 1186
DEFAULT_CONTENT_X = 1386
DEFAULT_FIRST_ROW_Y = 554
DEFAULT_ROW_GAP = 93
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


def key_code(code: int) -> None:
    ensure_dingtalk_frontmost()
    osascript(f'tell application "System Events" to key code {code}')


def keystroke(text: str) -> None:
    ensure_dingtalk_frontmost()
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    osascript(f'tell application "System Events" to keystroke "{escaped}"')


def select_all() -> None:
    ensure_dingtalk_frontmost()
    osascript('tell application "System Events" to keystroke "a" using command down')


def paste(text: str) -> None:
    ensure_dingtalk_frontmost()
    subprocess.run(["pbcopy"], input=text, text=True, check=True)
    osascript('tell application "System Events" to keystroke "v" using command down')


def load_rows(raw: str) -> list[dict[str, Any]]:
    rows = json.loads(raw)
    if not isinstance(rows, list):
        raise ValueError("--rows must be a JSON list")
    for row in rows:
        if not isinstance(row, dict) or "content" not in row:
            raise ValueError('Each row must be an object with a "content" field')
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Report date as yyyy-mm-dd.")
    parser.add_argument("--rows", required=True, help='JSON list, e.g. [{"content":"..."}].')
    parser.add_argument("--date-x", type=int, default=DEFAULT_DATE_X)
    parser.add_argument("--content-x", type=int, default=DEFAULT_CONTENT_X)
    parser.add_argument("--first-row-y", type=int, default=DEFAULT_FIRST_ROW_Y)
    parser.add_argument("--row-gap", type=int, default=DEFAULT_ROW_GAP)
    parser.add_argument("--driver", choices=["applescript", "cg"], default="cg")
    parser.add_argument("--scale-x", type=float, default=1.0)
    parser.add_argument("--scale-y", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Attempt Command+A before input. Leave off for empty new rows to avoid page-level selection.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = load_rows(args.rows)
    for index, row in enumerate(rows):
        y = args.first_row_y + index * args.row_gap
        print(f"row {index + 1}: date at {args.date_x},{y}; content at {args.content_x},{y}")
        if args.dry_run:
            continue
        click_point(args.date_x, y, args.driver, args.scale_x, args.scale_y)
        time.sleep(args.delay)
        if args.replace_existing:
            select_all()
        keystroke(args.date)
        time.sleep(args.delay)
        click_point(args.content_x, y, args.driver, args.scale_x, args.scale_y)
        time.sleep(args.delay)
        if args.replace_existing:
            select_all()
        paste(str(row["content"]))
        time.sleep(args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
