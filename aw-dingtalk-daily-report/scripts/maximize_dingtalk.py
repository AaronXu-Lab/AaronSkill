#!/usr/bin/env python3
"""Resize the DingTalk main window to the available Mac desktop area."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time


def run_osascript(script: str) -> str:
    result = subprocess.run(
        ["osascript", "-e", script],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def ensure_dingtalk_frontmost() -> None:
    subprocess.run(["open", "-a", "DingTalk"], text=True, capture_output=True, check=False)
    time.sleep(0.4)
    frontmost = run_osascript('tell application "System Events" to get name of first process whose frontmost is true')
    if frontmost == "DingTalk":
        return
    if frontmost in {"Codex", "Claude"} and os.environ.get("DINGTALK_ALLOW_ACTIVATE") == "1":
        subprocess.run(["osascript", "-e", 'tell application "DingTalk" to activate'], text=True, capture_output=True, check=False)
        time.sleep(0.4)
        frontmost = run_osascript('tell application "System Events" to get name of first process whose frontmost is true')
        if frontmost == "DingTalk":
            return
    raise RuntimeError(f"DingTalk is not frontmost; frontmost app is {frontmost or 'unknown'}")


def ensure_dingtalk_window(delay: float) -> None:
    ensure_dingtalk_frontmost()
    has_window = run_osascript(
        '''
tell application "System Events"
  tell process "DingTalk"
    if exists window 1 then
      return "yes"
    else
      return "no"
    end if
  end tell
end tell
'''
    )
    if has_window == "yes":
        return
    script = '''
tell application "System Events"
  tell process "DingTalk"
    tell menu bar item "窗口" of menu bar 1
      tell menu "窗口"
        if exists menu item "打开DING窗口" then
          click menu item "打开DING窗口"
        else if exists menu item "前置全部窗口" then
          click menu item "前置全部窗口"
        else
          error "No DingTalk window restore menu item found"
        end if
      end tell
    end tell
  end tell
end tell
'''
    run_osascript(script)
    time.sleep(delay)
    has_window = run_osascript(
        '''
tell application "System Events"
  tell process "DingTalk"
    if exists window 1 then
      return "yes"
    else
      return "no"
    end if
  end tell
end tell
'''
    )
    if has_window != "yes":
        raise RuntimeError("DingTalk window is still unavailable after restore attempt")


def parse_bounds(raw: str) -> tuple[int, int, int, int]:
    parts = [part.strip() for part in raw.replace(",", " ").split() if part.strip()]
    if len(parts) != 4:
        raise ValueError(f"Unexpected desktop bounds: {raw!r}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--menu-bar", type=int, default=24, help="Menu bar height to keep visible.")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay after activating DingTalk.")
    parser.add_argument("--dry-run", action="store_true", help="Print target bounds without resizing.")
    args = parser.parse_args()

    try:
        desktop_bounds = parse_bounds(
            run_osascript('tell application "Finder" to get bounds of window of desktop')
        )
        left, top, right, bottom = desktop_bounds
        target_left = left
        target_top = top + args.menu_bar
        target_width = right - left
        target_height = bottom - top - args.menu_bar

        payload = {
            "app": "DingTalk",
            "window": "frontmost window",
            "desktop_bounds": desktop_bounds,
            "target_position": [target_left, target_top],
            "target_size": [target_width, target_height],
            "dry_run": args.dry_run,
        }

        if not args.dry_run:
            ensure_dingtalk_window(args.delay)
            script = f'''
tell application "System Events"
  tell process "DingTalk"
    if exists window 1 then
      set position of window 1 to {{{target_left}, {target_top}}}
      set size of window 1 to {{{target_width}, {target_height}}}
    else
      error "DingTalk front window not found"
    end if
  end tell
end tell
'''
            run_osascript(script)

        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
