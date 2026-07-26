#!/usr/bin/env python3
"""Click absolute screen coordinates for staged DingTalk automation."""

from __future__ import annotations

import argparse
import os
import subprocess
import time


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


def click(x: int, y: int, delay: float) -> None:
    ensure_dingtalk_frontmost()
    osascript(
        f'tell application "System Events" to click at {{{x}, {y}}}',
    )
    if delay:
        time.sleep(delay)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("x", type=int)
    parser.add_argument("y", type=int)
    parser.add_argument("--clicks", type=int, default=1)
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args()

    for index in range(args.clicks):
        click(args.x, args.y, args.delay if index < args.clicks - 1 else 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
