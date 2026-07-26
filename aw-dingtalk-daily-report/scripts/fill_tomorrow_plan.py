#!/usr/bin/env python3
"""Paste 明日工作计划 into DingTalk after focusing or clicking a target field."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import time


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


def paste(text: str, replace_existing: bool) -> None:
    ensure_dingtalk_frontmost()
    subprocess.run(["pbcopy"], input=text, text=True, check=True)
    if replace_existing:
        osascript('tell application "System Events" to keystroke "a" using command down')
    osascript('tell application "System Events" to keystroke "v" using command down')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    parser.add_argument("--x", type=int, help="Optional plan field x coordinate.")
    parser.add_argument("--y", type=int, help="Optional plan field y coordinate.")
    parser.add_argument("--use-current-focus", action="store_true", help="Paste into the current focus. Use only after screenshot verification.")
    parser.add_argument("--driver", choices=["applescript", "cg"], default="cg")
    parser.add_argument("--scale-x", type=float, default=2.0)
    parser.add_argument("--scale-y", type=float, default=2.0)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Attempt Command+A before paste. Leave off for empty new fields to avoid page-level selection.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.x is not None or args.y is not None:
        if args.x is None or args.y is None:
            raise ValueError("--x and --y must be provided together")
        print(f"plan field: click {args.x},{args.y}")
    elif not args.use_current_focus:
        raise ValueError("Refusing to paste into unknown focus; pass --x/--y or --use-current-focus after verification.")
    else:
        print("plan field: use current focus")

    if args.dry_run:
        return 0
    if args.x is not None and args.y is not None:
        click_point(args.x, args.y, args.driver, args.scale_x, args.scale_y)
        time.sleep(args.delay)
    paste(args.text, args.replace_existing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
