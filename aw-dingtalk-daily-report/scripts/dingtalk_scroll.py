#!/usr/bin/env python3
"""Send a horizontal/vertical CGEvent scroll inside DingTalk."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import time


SWIFT_SOURCE = textwrap.dedent(
    """
    import CoreGraphics
    import Foundation

    let args = CommandLine.arguments
    if args.count < 5 {
      fputs("usage: scroll.swift x y horizontal vertical\\n", stderr)
      exit(2)
    }
    guard let x = Double(args[1]),
          let y = Double(args[2]),
          let horizontal = Int32(args[3]),
          let vertical = Int32(args[4]) else {
      fputs("invalid arguments\\n", stderr)
      exit(2)
    }

    CGWarpMouseCursorPosition(CGPoint(x: x, y: y))
    usleep(100_000)
    if let event = CGEvent(scrollWheelEvent2Source: nil, units: .pixel, wheelCount: 2, wheel1: vertical, wheel2: horizontal, wheel3: 0) {
      event.post(tap: .cghidEventTap)
    } else {
      fputs("failed to create scroll event\\n", stderr)
      exit(1)
    }
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--x", type=int, default=1450, help="Logical point x inside the table.")
    parser.add_argument("--y", type=int, default=590, help="Logical point y inside the table.")
    parser.add_argument("--horizontal", type=int, default=0, help="Horizontal pixel delta. Negative scrolls right in the DingTalk table.")
    parser.add_argument("--vertical", type=int, default=0, help="Vertical pixel delta.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"scroll at {args.x},{args.y}; horizontal={args.horizontal}; vertical={args.vertical}")
    if args.dry_run:
        return 0

    ensure_dingtalk_frontmost()
    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False) as handle:
        handle.write(SWIFT_SOURCE)
        swift_path = Path(handle.name)
    try:
        result = subprocess.run(
            ["/usr/bin/swift", str(swift_path), str(args.x), str(args.y), str(args.horizontal), str(args.vertical)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    finally:
        try:
            swift_path.unlink()
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
