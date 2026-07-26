---
name: aw-dingtalk-daily-report
description: Draft a DingTalk daily report in the macOS client through guarded, script-first automation. Use to prepare, dry-run, execute, diagnose, or retry report drafting while enforcing timeouts, app-focus checks, explicit stop points, manual review, and a strict no-submit boundary.
metadata:
  author: aaron_xu
  version: "0.2"
  creation_context: "基于 macOS 钉钉客户端中的真实日报填写流程创建，用脚本稳定准备日报草稿，同时保留人工检查并禁止自动提交。"
---

# AW DingTalk Daily Report

Prepare a complete draft and stop on the write-log page. The user always reviews and submits manually, even if their wording says “提交钉钉” or “推送钉钉,” unless they explicitly redefine this safety boundary.

## Required Runbook

Read `references/current-runbook.md` before running or debugging. Historical coordinates, experiments, and superseded flows are isolated in `references/legacy-debug-history-delete-after-next-run.md`; do not use them as instructions. After the next successful real run, remind the user that this legacy file can be deleted.

## Workflow

1. Convert the user's items into the report payload: date, rows with content/hours/progress, product line, project, and tomorrow plan.
2. Run `scripts/check_permissions.py`.
3. Run `scripts/run_daily_report_skill.py --dry-run --report-json '<json>'` and inspect the fixed result schema.
4. For real execution, start from a clean blank write-log draft and run the same entrypoint without `--dry-run`.
5. Stop at the first failed stage, timeout, focus loss, invalid payload, or explicit stop point.
6. On success, leave the completed page open, exit fullscreen, and return the fixed result schema. Never find or click Submit.

Use commands relative to the installed skill directory:

```bash
python3 scripts/run_daily_report_skill.py --dry-run --report-json '<json>'
python3 scripts/run_daily_report_skill.py --stop-after navigate --report-json '<json>'
python3 scripts/run_daily_report_skill.py --stage-timeout 90 --max-runtime 600 --report-json '<json>'
```

## Stop Conditions

Stop immediately when any condition is true:

- DingTalk is not frontmost after the one controlled activation attempt.
- required macOS permissions are unavailable;
- the write-log page is not positively identified;
- the draft is not blank at the expected start point;
- a date, dropdown value, row count, or payload field fails validation;
- any stage exceeds `--stage-timeout` or total execution exceeds `--max-runtime`;
- a script returns nonzero or requests visual localization;
- the requested `--stop-after` point is reached;
- the draft is filled and ready for manual review.

Do not silently switch to manual UI operations after a script failure. Computer Use is allowed only to localize a failure or when the user explicitly requests visual verification.

## Fixed Result Schema

Dry-run, stopped, success, and failure results must use these stable fields:

```json
{
  "ok": true,
  "mode": "dry-run|real",
  "status": "planned|stopped|ready-for-review|failed",
  "stopped_after": null,
  "submitted": false,
  "review_required": true,
  "log": "/absolute/path/to/last-run.jsonl",
  "script_actions": 0,
  "script_operation_units": 0,
  "fallbacks": 0,
  "legacy_cleanup_reminder": null
}
```

Additional error/count fields are allowed, but these fields and meanings are fixed. `submitted` must always remain `false`.

## Failure Handling

- Inspect `last-run.jsonl` and identify the first failed stage.
- If visual localization is needed, inspect only the failed state; do not finish the report manually.
- Update the current script or `references/current-runbook.md`, not the legacy history file.
- Retry only from a clean, positively verified starting state.
