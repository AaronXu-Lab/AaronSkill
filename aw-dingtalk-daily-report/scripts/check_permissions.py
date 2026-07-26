#!/usr/bin/env python3
"""Check local macOS permissions needed by DingTalk daily report automation."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile


def run(label: str, cmd: list[str], input_text: str | None = None) -> dict[str, object]:
    result = subprocess.run(cmd, input=input_text, text=True, capture_output=True, check=False)
    return {
        "check": label,
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout.strip()[:500],
        "stderr": result.stderr.strip()[:500],
    }


def main() -> int:
    checks: list[dict[str, object]] = []
    checks.append(run("osascript basic", ["osascript", "-e", 'return "ok"']))
    checks.append(
        run(
            "System Events frontmost query",
            ["osascript", "-e", 'tell application "System Events" to get name of first process whose frontmost is true'],
        )
    )
    checks.append(run("DingTalk activate", ["osascript", "-e", 'tell application "DingTalk" to activate']))
    checks.append(run("Clipboard write/read", ["bash", "-lc", "printf codex-permission-test | pbcopy && pbpaste"]))
    checks.append(run("Swift available", ["bash", "-lc", "command -v swift"]))

    swift_source = """
import CoreGraphics
import Foundation
let point = CGEvent(source: nil)?.location ?? CGPoint(x: -1, y: -1)
print("mouse=\\(Int(point.x)),\\(Int(point.y))")
guard let move = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: point, mouseButton: .left) else {
  exit(1)
}
move.post(tap: .cghidEventTap)
"""
    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False) as handle:
        handle.write(swift_source)
        swift_path = handle.name
    try:
        checks.append(run("Swift CoreGraphics mouseMoved post", ["/usr/bin/swift", swift_path]))
    finally:
        try:
            os.unlink(swift_path)
        except OSError:
            pass

    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if all(bool(check["ok"]) for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
