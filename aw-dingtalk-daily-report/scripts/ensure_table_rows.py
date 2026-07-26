#!/usr/bin/env python3
"""Ensure the DingTalk daily-report table has enough blank rows.

This script is intentionally simple: on a blank draft, DingTalk shows an empty
table with an 添加 button. Click that button once per desired row before any
field-filling script runs.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import time


SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_ADD_X = 1034
DEFAULT_ADD_Y = 706
DEFAULT_ADD_Y_STEP = -73


def osascript(script: str) -> str:
    result = subprocess.run(["osascript", "-e", script], text=True, capture_output=True, check=False)
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, required=True, help="Number of rows to add on a blank draft.")
    parser.add_argument("--add-x", type=int, default=DEFAULT_ADD_X)
    parser.add_argument("--add-y", type=int, default=DEFAULT_ADD_Y)
    parser.add_argument("--add-y-step", type=int, default=DEFAULT_ADD_Y_STEP, help="Y delta after each added row.")
    parser.add_argument("--scale-x", type=float, default=1.0)
    parser.add_argument("--scale-y", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.35)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.rows < 0:
        raise ValueError("--rows must be >= 0")

    for index in range(args.rows):
        y = args.add_y + index * args.add_y_step
        print(f"add row {index + 1}: click {args.add_x},{y}")
        if args.dry_run:
            continue
        cg_click(args.add_x, y, args.scale_x, args.scale_y)
        time.sleep(args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
