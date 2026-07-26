#!/usr/bin/env python3
"""Fill DingTalk daily report hours and progress columns from JSON."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from typing import Any


DEFAULT_HOURS_X = 646
DEFAULT_PROGRESS_X = 755
DEFAULT_FIRST_ROW_Y = 302
DEFAULT_ROW_GAP = 50


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


def paste(text: str, replace_existing: bool) -> None:
    ensure_dingtalk_frontmost()
    subprocess.run(["pbcopy"], input=text, text=True, check=True)
    if replace_existing:
        osascript('tell application "System Events" to keystroke "a" using command down')
    osascript('tell application "System Events" to keystroke "v" using command down')


def load_rows(raw: str) -> list[dict[str, Any]]:
    rows = json.loads(raw)
    if not isinstance(rows, list):
        raise ValueError("--rows must be a JSON list")
    for row in rows:
        if not isinstance(row, dict) or "hours" not in row or "progress" not in row:
            raise ValueError('Each row must include "hours" and "progress" fields')
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", required=True, help='JSON list, e.g. [{"hours":6,"progress":"80%"}].')
    parser.add_argument("--hours-x", type=int, default=DEFAULT_HOURS_X)
    parser.add_argument("--progress-x", type=int, default=DEFAULT_PROGRESS_X)
    parser.add_argument("--first-row-y", type=int, default=DEFAULT_FIRST_ROW_Y)
    parser.add_argument("--row-gap", type=int, default=DEFAULT_ROW_GAP)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Attempt Command+A before paste. Leave off for empty new rows to avoid page-level selection.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = load_rows(args.rows)
    for index, row in enumerate(rows):
        y = args.first_row_y + index * args.row_gap
        print(f"row {index + 1}: hours at {args.hours_x},{y}; progress at {args.progress_x},{y}")
        if args.dry_run:
            continue
        click(args.hours_x, y)
        time.sleep(args.delay)
        paste(str(row["hours"]), args.replace_existing)
        time.sleep(args.delay)
        click(args.progress_x, y)
        time.sleep(args.delay)
        paste(str(row["progress"]), args.replace_existing)
        time.sleep(args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
