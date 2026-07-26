#!/usr/bin/env python3
"""Script-first DingTalk daily report workflow runner.

The runner executes the skill's scriptable stages directly. It stops on the
first script failure and writes a JSONL trace so failures can be fed back into
the skill.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DEFAULT_LOG = ROOT / "last-run.jsonl"
LEGACY_HISTORY = ROOT / "references" / "legacy-debug-history-delete-after-next-run.md"
STAGE_TIMEOUT_SECONDS = 120.0
RUN_DEADLINE = float("inf")
SCREENSHOT_DIR: Path | None = None


DEFAULT_REPORT = {
    "date": "2026-06-30",
    "rows": [
        {
            "content": "梳理登录 alpha 1 信息架构与异常流程",
            "hours": 6,
            "progress": "80%",
        },
        {
            "content": "整理下月 AI 工具费用申请明细",
            "hours": 2,
            "progress": "100%",
        },
    ],
    "product_line": "其他",
    "project": "非交付投入",
    "tomorrow_plan": "整理 AXO 信息架构与构建 Roadmap",
}


class Trace:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.write_text("", encoding="utf-8")
        self.script_actions = 0
        self.script_operation_units = 0
        self.fallbacks = 0

    def write(self, event: dict[str, Any]) -> None:
        event.setdefault("ts", round(time.time(), 3))
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def script(self, stage: str, cmd: list[str], result: subprocess.CompletedProcess[str] | None = None) -> None:
        self.script_actions += 1
        operation_units = 1
        event: dict[str, Any] = {"kind": "script", "stage": stage, "cmd": cmd}
        if result is not None:
            operation_units = self._script_operation_units(result.stdout)
            event.update(
                {
                    "returncode": result.returncode,
                    "stdout": result.stdout.strip()[-1000:],
                    "stderr": result.stderr.strip()[-1000:],
                }
            )
            if operation_units != 1:
                event["script_operations"] = operation_units
        self.script_operation_units += operation_units
        self.write(event)

    def _script_operation_units(self, stdout: str) -> int:
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            operations = payload.get("script_operations")
            if isinstance(operations, int) and operations > 0:
                return operations
        return 1

    def fallback(self, stage: str, reason: str, next_script_target: str) -> None:
        self.fallbacks += 1
        self.write(
            {
                "kind": "fallback",
                "stage": stage,
                "reason": reason,
                "next_script_target": next_script_target,
            }
        )

    def summary(self) -> dict[str, Any]:
        total = self.script_actions + self.fallbacks
        operation_total = self.script_operation_units + self.fallbacks
        return {
            "script_actions": self.script_actions,
            "script_operation_units": self.script_operation_units,
            "fallbacks": self.fallbacks,
            "total_counted_events": total,
            "script_ratio": round(self.script_actions / total, 3) if total else 0,
            "operation_ratio": round(self.script_operation_units / operation_total, 3) if operation_total else 0,
        }


def run(stage: str, cmd: list[str], trace: Trace, dry_run: bool, dry_run_passthrough: bool = False) -> None:
    remaining = RUN_DEADLINE - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("maximum runtime exceeded before stage: " + stage)
    timeout = min(STAGE_TIMEOUT_SECONDS, remaining)
    if dry_run:
        if dry_run_passthrough:
            dry_cmd = [*cmd, "--dry-run"]
            result = subprocess.run(dry_cmd, text=True, capture_output=True, check=False, timeout=timeout)
            trace.script(stage, dry_cmd, result)
            print(f"[dry-run] {stage}: {' '.join(dry_cmd)}")
            print(result.stdout, end="")
            if result.returncode != 0:
                print(result.stderr, end="", file=sys.stderr)
                raise RuntimeError(f"dry-run stage failed: {stage}")
            return
        trace.script(stage, cmd)
        print(f"[dry-run] {stage}: {' '.join(cmd)}")
        return
    env = os.environ.copy()
    env.setdefault("DINGTALK_ALLOW_ACTIVATE", "1")
    result = subprocess.run(cmd, text=True, capture_output=True, check=False, env=env, timeout=timeout)
    trace.script(stage, cmd, result)
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(f"stage failed: {stage}")
    if SCREENSHOT_DIR is not None:
        screenshot_path = SCREENSHOT_DIR / f"{trace.script_actions:02d}-{stage.replace('/', '_')}.png"
        capture = subprocess.run(["screencapture", "-x", str(screenshot_path)], text=True, capture_output=True, check=False)
        trace.write({"kind": "screenshot", "stage": stage, "path": str(screenshot_path), "returncode": capture.returncode})
        if capture.returncode != 0:
            raise RuntimeError(f"failed to capture screenshot after stage: {stage}")


def script(name: str) -> str:
    return str(SCRIPTS / name)


def rows_json(report: dict[str, Any]) -> str:
    return json.dumps(report["rows"], ensure_ascii=False)


def visible_rows_json(report: dict[str, Any]) -> str:
    return json.dumps([{"content": row["content"]} for row in report["rows"]], ensure_ascii=False)


def report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False)


def main() -> int:
    global STAGE_TIMEOUT_SECONDS, RUN_DEADLINE, SCREENSHOT_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-json", help="Override report payload as JSON.")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stage-timeout", type=float, default=120.0, help="Maximum seconds for each helper stage.")
    parser.add_argument("--max-runtime", type=float, default=600.0, help="Maximum total runner seconds.")
    parser.add_argument("--reset-close-tabs", type=int, default=0, help="Press Command+W this many times before starting.")
    parser.add_argument("--skip-fullscreen", action="store_true")
    parser.add_argument("--skip-exit-fullscreen", action="store_true")
    parser.add_argument("--debug", action="store_true", help="Enable diagnostic artifacts such as stage screenshots.")
    parser.add_argument("--screenshot-dir", type=Path, help="Save a screenshot after each successful real stage; requires --debug.")
    parser.add_argument("--legacy-visible-flow", action="store_true", help="Use the older coordinate/scroll stage flow after opening the write-log page.")
    parser.add_argument("--stop-after", choices=["reset", "navigate", "blank-fill", "dates", "keyboard-core", "dropdowns", "tomorrow", "final"], help="Debug stop point.")
    args = parser.parse_args()

    if args.stage_timeout <= 0 or args.max_runtime <= 0:
        parser.error("--stage-timeout and --max-runtime must be positive")
    STAGE_TIMEOUT_SECONDS = args.stage_timeout
    RUN_DEADLINE = time.monotonic() + args.max_runtime
    if args.screenshot_dir is not None and not args.debug:
        parser.error("--screenshot-dir requires --debug")
    SCREENSHOT_DIR = args.screenshot_dir if args.debug else None
    if SCREENSHOT_DIR is not None:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    report = json.loads(args.report_json) if args.report_json else DEFAULT_REPORT
    trace = Trace(args.log)

    try:
        run("permissions", ["python3", script("check_permissions.py")], trace, args.dry_run)

        run("activate/maximize", ["python3", script("maximize_dingtalk.py")], trace, args.dry_run)
        if args.reset_close_tabs:
            run(
                "reset-close-tabs",
                [
                    "python3",
                    script("dingtalk_keys.py"),
                    "key",
                    "w",
                    "--modifier",
                    "command",
                    "--repeat",
                    str(args.reset_close_tabs),
                    "--delay",
                    "0.3",
                ],
                trace,
                args.dry_run,
            )
            run("restore-after-reset", ["python3", script("maximize_dingtalk.py")], trace, args.dry_run)
        if not args.skip_fullscreen:
            run("enter-fullscreen", ["python3", script("fullscreen_dingtalk.py"), "--action", "enter"], trace, args.dry_run)
        if args.stop_after == "reset":
            raise SystemExit(0)

        run("navigate-write-log", ["python3", script("open_write_log.py")], trace, args.dry_run)
        if args.stop_after == "navigate":
            raise SystemExit(0)

        if not args.legacy_visible_flow:
            run(
                "fill-blank-write-log-keyboard",
                [
                    "python3",
                    script("fill_blank_write_log_keyboard.py"),
                    "--report-json",
                    report_json(report),
                ],
                trace,
                args.dry_run,
                dry_run_passthrough=True,
            )
            if args.stop_after == "blank-fill":
                raise SystemExit(0)
            if not args.skip_exit_fullscreen:
                run("exit-fullscreen", ["python3", script("fullscreen_dingtalk.py"), "--action", "exit"], trace, args.dry_run)

            summary = trace.summary()
            trace.write({"kind": "summary", **summary})
            print(json.dumps({
                "ok": True,
                "mode": "dry-run" if args.dry_run else "real",
                "status": "planned" if args.dry_run else "ready-for-review",
                "stopped_after": None,
                "submitted": False,
                "review_required": True,
                "log": str(args.log),
                **summary,
                "legacy_cleanup_reminder": (str(LEGACY_HISTORY) if (not args.dry_run and LEGACY_HISTORY.exists()) else None),
            }, ensure_ascii=False, indent=2))
            return 0

        run(
            "ensure-table-rows",
            ["python3", script("ensure_table_rows.py"), "--rows", str(len(report["rows"]))],
            trace,
            args.dry_run,
        )

        run(
            "fill-dates-visible-fields",
            [
                "python3",
                script("fill_visible_rows.py"),
                "--date",
                str(report["date"]),
                "--rows",
                visible_rows_json(report),
            ],
            trace,
            args.dry_run,
        )
        if args.stop_after == "dates":
            raise SystemExit(0)

        run(
            "fill-visible-hours",
            ["python3", script("fill_visible_hours.py"), "--rows", rows_json(report)],
            trace,
            args.dry_run,
        )
        run(
            "scroll-to-progress-product",
            ["python3", script("dingtalk_scroll.py"), "--horizontal", "-450"],
            trace,
            args.dry_run,
        )
        run(
            "fill-progress-product",
            ["python3", script("fill_progress_product.py"), "--rows", rows_json(report)],
            trace,
            args.dry_run,
        )
        if args.stop_after == "keyboard-core":
            raise SystemExit(0)

        run(
            "scroll-to-project",
            ["python3", script("dingtalk_scroll.py"), "--horizontal", "-900"],
            trace,
            args.dry_run,
        )
        trace.fallback(
            "fill-project",
            "所属项目 dropdown coordinates are not script-safe yet; the latest calibration selected the wrong first-row item instead of 非交付投入.",
            "Recalibrate project dropdown on a clean blank draft before re-enabling fill_project.py in the runner.",
        )
        raise RuntimeError("fill-project stage is disabled until project dropdown selection is recalibrated")
        if args.stop_after == "dropdowns":
            raise SystemExit(0)

        trace.fallback(
            "tomorrow-plan",
            "Plan-field replacement is not script-safe yet; a coordinate trial selected the whole page instead of focusing the plan field.",
            "Add a script-detected plan-field focus before enabling fill_tomorrow_plan.py in the default runner.",
        )
        raise RuntimeError("tomorrow-plan stage is disabled until plan-field focus is script-safe")

        run(
            "tomorrow-plan",
            ["python3", script("fill_tomorrow_plan.py"), str(report["tomorrow_plan"])],
            trace,
            args.dry_run,
        )
        if args.stop_after == "tomorrow":
            raise SystemExit(0)

        if not args.skip_exit_fullscreen:
            run("exit-fullscreen", ["python3", script("fullscreen_dingtalk.py"), "--action", "exit"], trace, args.dry_run)

        summary = trace.summary()
        trace.write({"kind": "summary", **summary})
        print(json.dumps({
            "ok": True,
            "mode": "dry-run" if args.dry_run else "real",
            "status": "planned" if args.dry_run else "ready-for-review",
            "stopped_after": None,
            "submitted": False,
            "review_required": True,
            "log": str(args.log),
            **summary,
            "legacy_cleanup_reminder": (str(LEGACY_HISTORY) if (not args.dry_run and LEGACY_HISTORY.exists()) else None),
        }, ensure_ascii=False, indent=2))
        return 0
    except SystemExit:
        summary = trace.summary()
        trace.write({"kind": "stopped", **summary})
        print(json.dumps({
            "ok": True,
            "mode": "dry-run" if args.dry_run else "real",
            "status": "stopped",
            "stopped_after": args.stop_after,
            "submitted": False,
            "review_required": True,
            "log": str(args.log),
            **summary,
            "legacy_cleanup_reminder": None,
        }, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        trace.fallback("runner", str(exc), "Inspect last-run.jsonl and update the failing script stage before retrying.")
        summary = trace.summary()
        trace.write({"kind": "failed", "error": str(exc), **summary})
        print(json.dumps({
            "ok": False,
            "mode": "dry-run" if args.dry_run else "real",
            "status": "failed",
            "stopped_after": None,
            "submitted": False,
            "review_required": True,
            "error": str(exc),
            "log": str(args.log),
            **summary,
            "legacy_cleanup_reminder": None,
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
