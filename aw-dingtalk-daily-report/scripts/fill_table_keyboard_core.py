#!/usr/bin/env python3
"""Keyboard-first core fill for DingTalk daily report table.

This script keeps mouse usage to focus anchors only. Text entry, Tab traversal,
and progress entry use keyboard/clipboard because those steps were verified in
the fullscreen DingTalk report table.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


KEY_CODES = {
    "tab": 48,
    "space": 49,
}


DEFAULT_ROW1_WORK = (738, 292)
DEFAULT_ROW2_WORK = (738, 347)
DEFAULT_ROW1_HOUR = (812, 292)
DEFAULT_ROW2_HOUR = (812, 347)
DEFAULT_ROW1_PROGRESS = (737, 293)
SCRIPT_DIR = Path(__file__).resolve().parent


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


def click(point: tuple[int, int]) -> None:
    ensure_dingtalk_frontmost()
    x, y = point
    osascript(f'tell application "System Events" to click at {{{x}, {y}}}')


def cg_click(point: tuple[int, int], scale_x: float, scale_y: float) -> None:
    ensure_dingtalk_frontmost()
    x, y = point
    result = subprocess.run(
        ["python3", str(SCRIPT_DIR / "dingtalk_cg_click.py"), str(round(x * scale_x)), str(round(y * scale_y))],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "DINGTALK_ALLOW_ACTIVATE": os.environ.get("DINGTALK_ALLOW_ACTIVATE", "1")},
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def focus(point: tuple[int, int], driver: str, scale_x: float, scale_y: float) -> None:
    if driver == "cg":
        cg_click(point, scale_x, scale_y)
    else:
        click(point)


def key(name: str) -> None:
    ensure_dingtalk_frontmost()
    osascript(f'tell application "System Events" to key code {KEY_CODES[name]}')


def paste(text: str) -> None:
    ensure_dingtalk_frontmost()
    subprocess.run(["pbcopy"], input=text, text=True, check=True)
    osascript('tell application "System Events" to keystroke "v" using command down')


def type_text(text: str) -> None:
    ensure_dingtalk_frontmost()
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    osascript(f'tell application "System Events" to keystroke "{escaped}"')


def parse_point(raw: str) -> tuple[int, int]:
    parts = raw.split(",", 1)
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("point must be formatted as x,y")
    return int(parts[0]), int(parts[1])


def load_rows(raw: str) -> list[dict[str, Any]]:
    rows = json.loads(raw)
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("--rows must be a JSON list with exactly two rows")
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each row must be an object")
        for field in ("content", "hours", "progress"):
            if field not in row:
                raise ValueError(f'Each row must include "{field}"')
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", required=True, help='JSON list with content, hours, and progress for exactly two rows.')
    parser.add_argument("--row1-work", type=parse_point, default=DEFAULT_ROW1_WORK)
    parser.add_argument("--row2-work", type=parse_point, default=DEFAULT_ROW2_WORK)
    parser.add_argument("--row1-hour", type=parse_point, default=DEFAULT_ROW1_HOUR)
    parser.add_argument("--row2-hour", type=parse_point, default=DEFAULT_ROW2_HOUR)
    parser.add_argument("--row1-progress", type=parse_point, default=DEFAULT_ROW1_PROGRESS)
    parser.add_argument("--driver", choices=["applescript", "cg"], default="cg")
    parser.add_argument("--scale-x", type=float, default=2.0)
    parser.add_argument("--scale-y", type=float, default=2.0)
    parser.add_argument("--delay", type=float, default=0.18)
    parser.add_argument("--left-only", action="store_true", help="Fill only visible work/hour fields and skip the unsafe progress Tab path.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = load_rows(args.rows)
    steps = [
        ("click row 1 work", args.row1_work),
        ("paste row 1 work", rows[0]["content"]),
        ("click row 2 work", args.row2_work),
        ("paste row 2 work", rows[1]["content"]),
        ("click row 1 hour", args.row1_hour),
        ("type row 1 hour", str(rows[0]["hours"])),
        ("click row 2 hour", args.row2_hour),
        ("type row 2 hour", str(rows[1]["hours"])),
    ]
    if not args.left_only:
        steps.extend(
            [
                ("tab from row 2 hour to row 2 progress", None),
                ("type row 2 progress", str(rows[1]["progress"])),
                ("click row 1 progress", args.row1_progress),
                ("type row 1 progress", str(rows[0]["progress"])),
            ]
        )
    for label, value in steps:
        print(f"{label}: {value if value is not None else ''}")

    if args.dry_run:
        return 0

    focus(args.row1_work, args.driver, args.scale_x, args.scale_y)
    time.sleep(args.delay)
    paste(str(rows[0]["content"]))
    time.sleep(args.delay)
    focus(args.row2_work, args.driver, args.scale_x, args.scale_y)
    time.sleep(args.delay)
    paste(str(rows[1]["content"]))
    time.sleep(args.delay)

    focus(args.row1_hour, args.driver, args.scale_x, args.scale_y)
    time.sleep(args.delay)
    type_text(str(rows[0]["hours"]))
    time.sleep(args.delay)
    focus(args.row2_hour, args.driver, args.scale_x, args.scale_y)
    time.sleep(args.delay)
    type_text(str(rows[1]["hours"]))
    time.sleep(args.delay)

    if args.left_only:
        return 0

    key("tab")
    time.sleep(args.delay)
    type_text(str(rows[1]["progress"]))
    time.sleep(args.delay)
    focus(args.row1_progress, args.driver, args.scale_x, args.scale_y)
    time.sleep(args.delay)
    type_text(str(rows[0]["progress"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
