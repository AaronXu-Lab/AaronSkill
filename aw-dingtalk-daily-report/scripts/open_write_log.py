#!/usr/bin/env python3
"""Navigate DingTalk to 工作台 / 日志 / 写日志 using verified coordinate hints."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import time


DEFAULT_STEPS = [
    ("workbench", 9, 178, 1.5),
    # The 日志 application can take several seconds to render after it is
    # opened from 工作台; wait before attempting to locate + 写日志.
    ("log_app", 480, 113, 5.0),
    # A newly opened write-log page can show its editor shell before the table
    # control is interactive. Wait for the control tree to settle before the
    # keyboard-fill stage starts.
    ("write_log", 82, 85, 5.0),
]
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
    if result.returncode == 0 and os.environ.get("DINGTALK_ALLOW_ACTIVATE") == "1":
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


def parse_point(raw: str) -> tuple[int, int]:
    x_raw, y_raw = raw.split(",", 1)
    return int(x_raw), int(y_raw)


def detect_write_log_button(retina_scale: float) -> tuple[int, int] | None:
    """Find the blue '+ 写日志' button in a Retina screenshot.

    DingTalk's titlebar/fullscreen state shifts the y coordinate by roughly one
    titlebar. Pixel detection is more stable than a fixed hand-tuned point for
    this top-left navigation button.
    """
    try:
        from PIL import Image
    except Exception:
        return None

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        screenshot_path = Path(handle.name)
    try:
        result = subprocess.run(["screencapture", "-x", str(screenshot_path)], text=True, capture_output=True, check=False)
        if result.returncode != 0:
            return None
        image = Image.open(screenshot_path).convert("RGB")
        width, height = image.size
        max_x = min(width, int(650 * retina_scale))
        max_y = min(height, int(260 * retina_scale))
        mask: set[tuple[int, int]] = set()
        for y in range(0, max_y):
            for x in range(0, max_x):
                r, g, b = image.getpixel((x, y))
                if r < 100 and 60 < g < 195 and b > 170:
                    mask.add((x, y))

        seen: set[tuple[int, int]] = set()
        best: tuple[int, int, int, int, int] | None = None
        for point in list(mask):
            if point in seen:
                continue
            stack = [point]
            seen.add(point)
            xs: list[int] = []
            ys: list[int] = []
            while stack:
                x, y = stack.pop()
                xs.append(x)
                ys.append(y)
                for nx in (x - 1, x, x + 1):
                    for ny in (y - 1, y, y + 1):
                        neighbor = (nx, ny)
                        if neighbor in mask and neighbor not in seen:
                            seen.add(neighbor)
                            stack.append(neighbor)
            if not xs:
                continue
            x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
            component_width = x2 - x1 + 1
            component_height = y2 - y1 + 1
            area = len(xs)
            if component_width < int(120 * retina_scale) or component_height < int(22 * retina_scale):
                continue
            candidate = (area, x1, y1, x2, y2)
            if best is None or candidate[0] > best[0]:
                best = candidate

        if best is None:
            return None
        _, x1, y1, x2, y2 = best
        return round(((x1 + x2) / 2) / retina_scale), round(((y1 + y2) / 2) / retina_scale)
    finally:
        try:
            screenshot_path.unlink()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbench", default="9,178", help="工作台 click point as x,y before CG scaling.")
    parser.add_argument("--log-app", default="480,113", help="日志 app click point as x,y before CG scaling.")
    parser.add_argument("--write-log", default="82,85", help="写日志 click point as x,y before CG scaling.")
    parser.add_argument("--driver", choices=["applescript", "cg"], default="cg")
    parser.add_argument("--scale-x", type=float, default=2.0, help="Coordinate multiplier for CGEvent.")
    parser.add_argument("--scale-y", type=float, default=2.0, help="Coordinate multiplier for CGEvent.")
    parser.add_argument("--retina-scale", type=float, default=2.0, help="Retina screenshot scale used by button detection.")
    parser.add_argument("--no-detect-write-log", action="store_true", help="Disable screenshot-based 写日志 button detection.")
    parser.add_argument("--step-delay", type=float, default=None, help="Override delay after every click.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    points = {
        "workbench": parse_point(args.workbench),
        "log_app": parse_point(args.log_app),
        "write_log": parse_point(args.write_log),
    }

    for name, _x, _y, default_delay in DEFAULT_STEPS:
        x, y = points[name]
        detected = False
        if name == "write_log" and args.driver == "cg" and not args.no_detect_write_log and not args.dry_run:
            detected_point = detect_write_log_button(args.retina_scale)
            if detected_point is not None:
                x, y = detected_point
                detected = True
        delay = default_delay if args.step_delay is None else args.step_delay
        source = "detected" if detected else "configured"
        print(f"{name}: click {x},{y} ({source}); wait {delay}s")
        if not args.dry_run:
            if args.driver == "cg" and detected:
                cg_click(x, y)
            elif args.driver == "cg":
                cg_click(round(x * args.scale_x), round(y * args.scale_y))
            else:
                click(x, y)
            time.sleep(delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
