#!/usr/bin/env python3
"""Fill visible 工时 cells in the DingTalk daily-report table."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_HOUR_X = 1518
DEFAULT_FIRST_ROW_Y = 554
DEFAULT_ROW_GAP = 93


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
    if os.environ.get("DINGTALK_ALLOW_ACTIVATE") == "1":
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
    osascript('tell application "System Events" to keystroke "a" using command down')
    time.sleep(0.05)
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    osascript(f'tell application "System Events" to keystroke "{escaped}"')


def load_rows(raw: str) -> list[dict[str, Any]]:
    rows = json.loads(raw)
    if not isinstance(rows, list):
        raise ValueError("--rows must be a JSON list")
    for row in rows:
        if not isinstance(row, dict) or "hours" not in row:
            raise ValueError('Each row must include "hours"')
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", required=True, help='JSON list with "hours" values.')
    parser.add_argument("--hour-x", type=int, default=DEFAULT_HOUR_X)
    parser.add_argument("--first-row-y", type=int, default=DEFAULT_FIRST_ROW_Y)
    parser.add_argument("--row-gap", type=int, default=DEFAULT_ROW_GAP)
    parser.add_argument("--scale-x", type=float, default=1.0)
    parser.add_argument("--scale-y", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = load_rows(args.rows)
    for index, row in enumerate(rows):
        y = args.first_row_y + index * args.row_gap
        print(f"row {index + 1}: hours at {args.hour_x},{y}")
        if args.dry_run:
            continue
        cg_click(args.hour_x, y, args.scale_x, args.scale_y)
        time.sleep(args.delay)
        replace_text(str(row["hours"]))
        time.sleep(args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
