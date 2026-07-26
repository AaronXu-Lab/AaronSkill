#!/usr/bin/env python3
"""Fill a blank DingTalk write-log page with a keyboard-first flow.

Assumptions:
- DingTalk is already on a blank 产品创新部日报 write-log page.
- Screen coordinates are the logical 2560x1440 coordinate space used by
  CGEvent on the user's display.
- The table starts empty; rows are added before table entry.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import time
from typing import Any


DEFAULT_FIRST_ADD_X = 1033
DEFAULT_FIRST_ADD_Y = 705
DEFAULT_SECOND_ADD_Y = 633
DEFAULT_THIRD_ADD_Y = 726
DEFAULT_ADD_Y_STEP = 93
DEFAULT_DATE_X = 1181
DEFAULT_DATE_Y = 555

SHELL_APPS = {"Codex", "Claude"}

SWIFT_CLICK_SOURCE = textwrap.dedent(
    """
    import CoreGraphics
    import Foundation

    if CommandLine.arguments.count != 3 && CommandLine.arguments.count != 4 {
      fputs("usage: click x y [move]\\n", stderr)
      exit(2)
    }
    guard let x = Double(CommandLine.arguments[1]),
          let y = Double(CommandLine.arguments[2]) else {
      fputs("invalid coordinates\\n", stderr)
      exit(2)
    }
    let point = CGPoint(x: x, y: y)
    if CommandLine.arguments.count == 4 && CommandLine.arguments[3] == "move" {
      CGWarpMouseCursorPosition(point)
      exit(0)
    }
    guard let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left),
          let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left) else {
      fputs("failed to create mouse events\\n", stderr)
      exit(1)
    }
    down.post(tap: .cghidEventTap)
    usleep(60_000)
    up.post(tap: .cghidEventTap)
    """
)

KEY_CODES = {
    "enter": 36,
    "return": 36,
    "tab": 48,
    "down": 125,
}

SCRIPT_OPERATIONS = 0


def count_operation() -> None:
    global SCRIPT_OPERATIONS
    SCRIPT_OPERATIONS += 1


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
    if frontmost in SHELL_APPS and os.environ.get("DINGTALK_ALLOW_ACTIVATE") == "1":
        subprocess.run(["osascript", "-e", 'tell application "DingTalk" to activate'], text=True, capture_output=True, check=False)
        time.sleep(0.4)
        frontmost = osascript('tell application "System Events" to get name of first process whose frontmost is true')
        if frontmost == "DingTalk":
            return
    raise RuntimeError(f"DingTalk is not frontmost; frontmost app is {frontmost or 'unknown'}")


class Clicker:
    def __init__(self, dry_run: bool) -> None:
        self.dry_run = dry_run
        self._exe: Path | None = None
        self._tmpdir: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> "Clicker":
        if self.dry_run:
            return self
        self._tmpdir = tempfile.TemporaryDirectory()
        tmpdir = Path(self._tmpdir.name)
        swift_path = tmpdir / "click.swift"
        exe_path = tmpdir / "click"
        swift_path.write_text(SWIFT_CLICK_SOURCE, encoding="utf-8")
        result = subprocess.run(["/usr/bin/swiftc", str(swift_path), "-o", str(exe_path)], text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        self._exe = exe_path
        return self

    def __exit__(self, *_: object) -> None:
        if self._tmpdir is not None:
            self._tmpdir.cleanup()

    def click(self, x: int, y: int) -> None:
        print(f"click {x},{y}")
        count_operation()
        if self.dry_run:
            return
        ensure_dingtalk_frontmost()
        if self._exe is None:
            raise RuntimeError("click helper is not compiled")
        result = subprocess.run([str(self._exe), str(x), str(y)], text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())

    def move(self, x: int, y: int) -> None:
        print(f"move {x},{y}")
        count_operation()
        if self.dry_run:
            return
        ensure_dingtalk_frontmost()
        if self._exe is None:
            raise RuntimeError("click helper is not compiled")
        result = subprocess.run([str(self._exe), str(x), str(y), "move"], text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def set_clipboard(text: str) -> None:
    subprocess.run(["pbcopy"], input=text, text=True, check=True)


def paste(text: str, dry_run: bool, delay: float) -> None:
    print(f"paste {text}")
    count_operation()
    if dry_run:
        return
    ensure_dingtalk_frontmost()
    set_clipboard(text)
    time.sleep(delay)
    osascript('tell application "System Events" to keystroke "v" using command down')


def key(name: str, dry_run: bool, repeat: int = 1, delay: float = 0.06) -> None:
    if name not in KEY_CODES:
        raise ValueError(f"unknown key: {name}")
    print(f"key {name}" + (f" x{repeat}" if repeat != 1 else ""))
    for _ in range(repeat):
        count_operation()
    if dry_run:
        return
    ensure_dingtalk_frontmost()
    code = KEY_CODES[name]
    for index in range(repeat):
        osascript(f'tell application "System Events" to key code {code}')
        if index < repeat - 1:
            time.sleep(delay)


def add_y_for_index(index: int, first_y: int, second_y: int, third_y: int, step: int) -> int:
    if index == 0:
        return first_y
    if index == 1:
        return second_y
    return third_y + (index - 2) * step


def load_report(raw: str) -> dict[str, Any]:
    report = json.loads(raw)
    if not isinstance(report, dict):
        raise ValueError("--report-json must be a JSON object")
    rows = report.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError('report must contain a non-empty "rows" list')
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each row must be an object")
        for key_name in ("content", "hours", "progress"):
            if key_name not in row:
                raise ValueError(f'each row must contain "{key_name}"')
    if not report.get("date"):
        raise ValueError('report must contain "date"')
    if not report.get("tomorrow_plan"):
        raise ValueError('report must contain "tomorrow_plan"')
    product_line = report.get("product_line", "其他")
    if product_line not in {"其他", "其它"}:
        raise ValueError("keyboard dropdown path currently supports only 产品线=其他/其它")
    if report.get("project", "非交付投入") != "非交付投入":
        raise ValueError("keyboard dropdown path currently supports only 所属项目=非交付投入")
    return report


def fill_row(row: dict[str, Any], dry_run: bool, delay: float, advance_to_customer: bool) -> None:
    key("tab", dry_run, delay=delay)
    paste(str(row["content"]), dry_run, delay)

    key("tab", dry_run, delay=delay)
    paste(str(row["hours"]), dry_run, delay)

    key("tab", dry_run, delay=delay)
    paste(str(row["progress"]), dry_run, delay)

    key("tab", dry_run, delay=delay)
    key("down", dry_run, delay=delay)
    key("enter", dry_run, delay=delay)

    key("tab", dry_run, delay=delay)
    key("down", dry_run, repeat=2, delay=delay)
    key("enter", dry_run, delay=delay)

    if advance_to_customer:
        key("tab", dry_run, delay=delay)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-json", required=True, help="Report payload JSON.")
    parser.add_argument("--tabs-from-last-project-to-plan", type=int, default=3)
    parser.add_argument("--skip-add-rows", action="store_true", help="Fill pre-existing blank rows without clicking 添加.")
    parser.add_argument("--skip-tomorrow-plan", action="store_true", help="Stop after table rows without editing 明日工作计划.")
    parser.add_argument("--add-x", type=int, default=DEFAULT_FIRST_ADD_X)
    parser.add_argument("--first-add-y", type=int, default=DEFAULT_FIRST_ADD_Y)
    parser.add_argument("--second-add-y", type=int, default=DEFAULT_SECOND_ADD_Y)
    parser.add_argument("--third-add-y", type=int, default=DEFAULT_THIRD_ADD_Y)
    parser.add_argument("--add-y-step", type=int, default=DEFAULT_ADD_Y_STEP)
    parser.add_argument("--date-x", type=int, default=DEFAULT_DATE_X)
    parser.add_argument("--date-y", type=int, default=DEFAULT_DATE_Y)
    parser.add_argument("--mouse-park-x", type=int, default=10)
    parser.add_argument("--mouse-park-y", type=int, default=10)
    parser.add_argument("--delay", type=float, default=0.12)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    report = load_report(args.report_json)
    rows = report["rows"]
    date = str(report["date"])

    if not args.dry_run:
        ensure_dingtalk_frontmost()

    with Clicker(args.dry_run) as clicker:
        if not args.skip_add_rows:
            for index in range(len(rows)):
                y = add_y_for_index(index, args.first_add_y, args.second_add_y, args.third_add_y, args.add_y_step)
                clicker.click(args.add_x, y)
                time.sleep(args.delay)

        clicker.click(args.date_x, args.date_y)
        time.sleep(args.delay)
        clicker.move(args.mouse_park_x, args.mouse_park_y)
        time.sleep(args.delay)

        for index, row in enumerate(rows):
            if index > 0:
                key("tab", args.dry_run, delay=args.delay)
                key("enter", args.dry_run, delay=args.delay)
            paste(date, args.dry_run, args.delay)
            key("enter", args.dry_run, delay=args.delay)
            fill_row(row, args.dry_run, args.delay, advance_to_customer=index < len(rows) - 1)

        if not args.skip_tomorrow_plan:
            key("tab", args.dry_run, repeat=args.tabs_from_last_project_to_plan, delay=args.delay)
            paste(str(report["tomorrow_plan"]), args.dry_run, args.delay)
    print(json.dumps({"script_operations": SCRIPT_OPERATIONS}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
