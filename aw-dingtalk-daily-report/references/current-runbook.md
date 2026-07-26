# Current DingTalk Daily Report Runbook

## Entry point

Use `scripts/run_daily_report_skill.py`. It resolves all helper paths relative to the installed skill directory, so the skill may move or be renamed without changing absolute paths.

The default flow is:

1. permission check;
2. activate and maximize DingTalk;
3. optionally enter fullscreen;
4. navigate to the blank write-log page;
5. add and fill rows through `fill_blank_write_log_keyboard.py`;
6. fill tomorrow's plan;
7. exit fullscreen;
8. stop for manual review without submitting.

Navigation waits five seconds after opening 日志 from 工作台 before locating
and clicking `+ 写日志`, then waits five seconds for the write-log table
control to become interactive before any keyboard entry begins.

## Preconditions

- The macOS Accessibility, Automation, and screen/clipboard permissions required by the scripts are granted.
- The user has a clean blank draft. Retained content is contaminated test data.
- The write-log table coordinates are specified in the logical 2560×1440 CGEvent coordinate space; do not Retina-scale them again before clicking.
- Product line is `其他/其它` and project is `非交付投入`; extend and verify dropdown logic before using other values.
- Dates use `yyyy-mm-dd`; default to yesterday unless the user specifies another date.

## Guardrails

- Each helper checks or relies on the DingTalk frontmost-app guard.
- The runner performs at most one controlled DingTalk activation using `DINGTALK_ALLOW_ACTIVATE=1`.
- `--stage-timeout` limits each helper; `--max-runtime` limits the whole run.
- `--stop-after` supports staged debugging without continuing into later actions.
- A helper failure produces a trace and stops the run.
- No script in this workflow may click the final Submit control.
- Stage screenshots are diagnostic-only: enable them explicitly with `--debug --screenshot-dir <directory>`; normal runs do not capture screenshots.

## Diagnosis

Read `last-run.jsonl` from top to bottom and locate the first `failed` or `fallback` event. Record the stage, error, and next script target. Use visual inspection only to localize that state, then update the responsible script and retry from a clean draft.

## Legacy cleanup

`legacy-debug-history-delete-after-next-run.md` contains superseded coordinates, debugging history, and old flow descriptions. After one successful real run of version 0.2, tell the user it is safe to delete that file; do not delete it automatically.
