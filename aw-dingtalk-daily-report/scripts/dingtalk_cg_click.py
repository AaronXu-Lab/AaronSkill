#!/usr/bin/env python3
"""Click screen coordinates using macOS CGEvent via Swift.

System Events `click at` can miss DingTalk's Chromium surfaces. CGEvent posts a
lower-level mouse down/up pair and has been more reliable for fixed navigation
anchors.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import textwrap
import time


SWIFT_SOURCE = textwrap.dedent(
    """
    import CoreGraphics
    import Foundation

    let args = CommandLine.arguments
    if args.count < 3 {
      fputs("usage: click.swift x y\\n", stderr)
      exit(2)
    }
    guard let x = Double(args[1]), let y = Double(args[2]) else {
      fputs("invalid coordinates\\n", stderr)
      exit(2)
    }
    let point = CGPoint(x: x, y: y)
    guard let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left),
          let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left) else {
      fputs("failed to create mouse events\\n", stderr)
      exit(1)
    }
    down.post(tap: .cghidEventTap)
    usleep(80_000)
    up.post(tap: .cghidEventTap)
    """
)


def osascript(script: str) -> str:
    result = subprocess.run(["osascript", "-e", script], text=True, capture_output=True, check=False)
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


def cg_click(x: int, y: int) -> None:
    ensure_dingtalk_frontmost()
    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False) as handle:
        handle.write(SWIFT_SOURCE)
        swift_path = handle.name
    try:
        result = subprocess.run(["/usr/bin/swift", swift_path, str(x), str(y)], text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    finally:
        try:
            os.unlink(swift_path)
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("x", type=int)
    parser.add_argument("y", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"cg-click {args.x},{args.y}")
    if args.dry_run:
        return 0
    try:
        cg_click(args.x, args.y)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
