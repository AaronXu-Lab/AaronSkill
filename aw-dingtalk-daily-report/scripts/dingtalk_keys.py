#!/usr/bin/env python3
"""Send keyboard and clipboard input to the active DingTalk window."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time


KEY_CODES = {
    "enter": 36,
    "return": 36,
    "tab": 48,
    "space": 49,
    "escape": 53,
    "esc": 53,
    "delete": 51,
    "backspace": 51,
    "left": 123,
    "right": 124,
    "down": 125,
    "up": 126,
    "w": 13,
    "f": 3,
}

MODIFIERS = {
    "command": "command down",
    "cmd": "command down",
    "control": "control down",
    "ctrl": "control down",
    "option": "option down",
    "alt": "option down",
    "shift": "shift down",
}


def osascript(*lines: str) -> None:
    args: list[str] = ["osascript"]
    for line in lines:
        args.extend(["-e", line])
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def ensure_dingtalk_frontmost() -> None:
    result = subprocess.run(
        ["osascript", "-e", 'tell application "System Events" to get name of first process whose frontmost is true'],
        text=True,
        capture_output=True,
        check=False,
    )
    frontmost = result.stdout.strip()
    if result.returncode == 0 and frontmost == "DingTalk":
        return
    if result.returncode == 0 and frontmost in {"Codex", "Claude"} and os.environ.get("DINGTALK_ALLOW_ACTIVATE") == "1":
        subprocess.run(["osascript", "-e", 'tell application "DingTalk" to activate'], text=True, capture_output=True, check=False)
        time.sleep(0.4)
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to get name of first process whose frontmost is true'],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip() == "DingTalk":
            return
    raise RuntimeError(f"DingTalk is not frontmost; frontmost app is {frontmost or 'unknown'}")


def set_clipboard(text: str) -> None:
    subprocess.run(["pbcopy"], input=text, text=True, check=True)


def paste(text: str, delay: float) -> None:
    ensure_dingtalk_frontmost()
    set_clipboard(text)
    time.sleep(delay)
    osascript('tell application "System Events" to keystroke "v" using command down')


def type_text(text: str) -> None:
    ensure_dingtalk_frontmost()
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    osascript(f'tell application "System Events" to keystroke "{escaped}"')


def select_all() -> None:
    ensure_dingtalk_frontmost()
    osascript('tell application "System Events" to keystroke "a" using command down')


def key(name: str, repeat: int, delay: float, modifiers: list[str] | None = None) -> None:
    if name not in KEY_CODES:
        valid = ", ".join(sorted(KEY_CODES))
        raise ValueError(f"Unknown key {name!r}. Valid keys: {valid}")
    ensure_dingtalk_frontmost()
    code = KEY_CODES[name]
    using_clause = ""
    if modifiers:
        resolved = []
        for modifier in modifiers:
            if modifier not in MODIFIERS:
                valid = ", ".join(sorted(MODIFIERS))
                raise ValueError(f"Unknown modifier {modifier!r}. Valid modifiers: {valid}")
            resolved.append(MODIFIERS[modifier])
        using_clause = " using {" + ", ".join(resolved) + "}"
    for index in range(repeat):
        osascript(f'tell application "System Events" to key code {code}{using_clause}')
        if index < repeat - 1:
            time.sleep(delay)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    paste_parser = subparsers.add_parser("paste", help="Paste text through the clipboard.")
    paste_parser.add_argument("text")
    paste_parser.add_argument("--delay", type=float, default=0.1)

    type_parser = subparsers.add_parser("type", help="Type short ASCII text.")
    type_parser.add_argument("text")

    subparsers.add_parser("select-all", help="Press Command+A.")

    key_parser = subparsers.add_parser("key", help="Press a named key.")
    key_parser.add_argument("name", choices=sorted(KEY_CODES))
    key_parser.add_argument("--repeat", type=int, default=1)
    key_parser.add_argument("--delay", type=float, default=0.05)
    key_parser.add_argument(
        "--modifier",
        action="append",
        choices=sorted(MODIFIERS),
        help="Modifier to hold while pressing the key. Repeat for combinations.",
    )

    args = parser.parse_args()
    try:
        if args.command == "paste":
            paste(args.text, args.delay)
        elif args.command == "type":
            type_text(args.text)
        elif args.command == "select-all":
            select_all()
        elif args.command == "key":
            key(args.name, args.repeat, args.delay, args.modifier)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
