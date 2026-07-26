#!/usr/bin/env python3
"""Enter or exit native macOS fullscreen for DingTalk when the workflow needs it."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time


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


def menu_enter_fullscreen(delay: float) -> None:
    ensure_dingtalk_frontmost()
    script = f'''
delay {delay}
tell application "System Events"
  tell process "DingTalk"
    tell menu bar 1
      tell menu bar item "窗口"
        tell menu "窗口"
          if exists menu item "进入全屏幕" then
            click menu item "进入全屏幕"
          else if exists menu item "进入全屏" then
            click menu item "进入全屏"
          else if exists menu item "Enter Full Screen" then
            click menu item "Enter Full Screen"
          else if exists menu item "全屏幕" then
            click menu item "全屏幕"
          else
            error "No fullscreen menu item found"
          end if
        end tell
      end tell
    end tell
  end tell
end tell
'''
    osascript(script)


def menu_exit_fullscreen(delay: float) -> bool:
    ensure_dingtalk_frontmost()
    script = f'''
delay {delay}
tell application "System Events"
  tell process "DingTalk"
    tell menu bar 1
      tell menu bar item "窗口"
        tell menu "窗口"
          if exists menu item "退出全屏幕" then
            click menu item "退出全屏幕"
            return "clicked"
          else if exists menu item "退出全屏" then
            click menu item "退出全屏"
            return "clicked"
          else if exists menu item "Exit Full Screen" then
            click menu item "Exit Full Screen"
            return "clicked"
          else
            return "not-fullscreen"
          end if
        end tell
      end tell
    end tell
  end tell
end tell
'''
    result = osascript(script)
    return result == "clicked"


def shortcut_fullscreen(delay: float) -> None:
    # macOS default for Enter Full Screen is Control+Command+F. The user may
    # press Control+Fn+F manually, but AppleScript cannot synthesize Fn
    # reliably, so the script uses the system shortcut equivalent.
    ensure_dingtalk_frontmost()
    osascript(
        f"delay {delay}",
        'tell application "System Events" to key code 3 using {control down, command down}',
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        choices=["enter", "exit"],
        default="enter",
        help="Enter or exit native fullscreen. Exit uses the Window menu only and will not toggle into fullscreen.",
    )
    parser.add_argument(
        "--method",
        choices=["menu", "shortcut", "auto"],
        default="auto",
        help="Fullscreen method. auto tries the Window menu, then Control+Command+F. Control+Fn+F is a manual fallback.",
    )
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = {"app": "DingTalk", "action": args.action, "method": args.method}
    if args.dry_run:
        payload["dry_run"] = True
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    try:
        if args.action == "exit":
            did_exit = menu_exit_fullscreen(args.delay)
            payload["used"] = "menu"
            payload["result"] = "exited" if did_exit else "already-not-fullscreen"
        elif args.method == "menu":
            menu_enter_fullscreen(args.delay)
            payload["used"] = "menu"
        elif args.method == "shortcut":
            shortcut_fullscreen(args.delay)
            payload["used"] = "shortcut"
        else:
            try:
                menu_enter_fullscreen(args.delay)
                payload["used"] = "menu"
            except Exception as menu_error:
                shortcut_fullscreen(args.delay)
                payload["used"] = "shortcut"
                payload["menu_error"] = str(menu_error)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
