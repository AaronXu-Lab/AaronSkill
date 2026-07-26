# DingTalk Daily Report Keyboard Flow

## Run cadence

Prefer `scripts/run_daily_report_skill.py` to run the stable script-first flow end to end. The runner no longer emits routine Computer Use verification checkpoints. Use Computer Use only when a script fails and visual failure localization is needed, or when the user explicitly asks for a visual check.

Blank-draft rule: DingTalk retains partially entered logs. Old runs that relied on retained draft content are not valid verification. For clean verification, the user or script must start from a blank write-log page. A blank page has no table rows and no tomorrow-plan content.

Every script should stop if DingTalk is not the frontmost app. The only controlled exception is when Codex becomes frontmost because the shell command is being launched while DingTalk is ready in the background. In that case, prefix the command with `DINGTALK_ALLOW_ACTIVATE=1`; the scripts only allow that recovery from `Codex`, then re-check that `DingTalk` is frontmost before clicking or typing.

Recommended permission check:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/check_permissions.py
```

Recommended dry-run:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/run_daily_report_skill.py --dry-run
```

Optional staged run while iterating:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/run_daily_report_skill.py --stop-after navigate
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/run_daily_report_skill.py --stop-after blank-fill
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/run_daily_report_skill.py
```

The runner writes `last-run.jsonl` with these event types:

- `script`: a script executed or would execute in dry-run mode.
- `fallback`: a script failure or script gap that must be converted into a future script improvement.
- `summary`, `failed`, or `stopped`: final accounting for the run.

For real runs, `fill_blank_write_log_keyboard.py` emits `{"script_operations": N}` and the runner includes `script_operation_units` in the final summary.

Do not rely on Computer Use element indexes inside the DingTalk HTML report iframe. The accessibility tree can expose indexes such as table cells and text inputs, but `click` or `set_value` may reject them as invalid element IDs. Use the scripted coordinate and keyboard flow instead.

In native fullscreen, do not rely on Python scripts that use AppleScript `click at` for table field entry. A verified failure showed `fill_visible_rows.py` returned success while the page remained empty. Use the CGEvent-backed click driver plus keyboard/clipboard entry for fullscreen field entry. Computer Use should only localize failures, not perform routine data entry.

## Current default: blank write-log keyboard flow

After `open_write_log.py` reaches the blank write-log page, the default runner calls:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/fill_blank_write_log_keyboard.py \
  --report-json '{"date":"2026-06-30","rows":[{"content":"梳理登录 alpha 1 信息架构与异常流程","hours":6,"progress":"80%"},{"content":"整理下月 AI 工具费用申请明细","hours":2,"progress":"100%"}],"product_line":"其他","project":"非交付投入","tomorrow_plan":"整理 AXO 信息架构与构建 Roadmap"}'
```

User-supplied assumptions for the production flow:

- Display coordinate space: 2560x1440 logical screen coordinates. `screencapture` may produce 5120x2880 Retina pixels, but the CGEvent click coordinates should use the 2560x1440 values below unless the next screenshot contradicts this.
- The blank write-log page starts with all fields empty.
- Add button coordinates:
  - Row 1: `(1033,705)`.
  - Row 2: `(1033,633)`.
  - Row 3: `(1033,726)`.
  - Row 4+: same x, y += `93`.
- First row date field: `(1181,555)`.
- For row 1, click the date field, type/paste `yyyy-mm-dd`, then press Enter to confirm the active date field.
- After the first date field click, immediately move the mouse to `(10,10)` before keyboard-driven table entry. A real run selected the wrong first-row 所属项目, likely because the mouse hover changed the active dropdown item.
- Press Tab to 工作事项, paste the content.
- Press Tab to 工时, paste the hour value.
- Press Tab to 进度, paste the progress value.
- Press Tab to 产品线, press Down once, then Enter. The dropdown should land on first item `其他`.
- Press Tab to 所属项目, press Down twice, then Enter. This should select second item `非交付投入`.
- For non-final rows, press Tab to 自填客户名称和商机编号 and leave it empty, then press Tab to the next row. If another report item exists, press Enter to activate the next date field, then repeat the date/content/hour/progress/dropdown sequence.
- On the final row, stop after confirming 所属项目. Press Tab three times to focus 明日工作计划, then paste the plan text.

The script intentionally rejects other 产品线 or 所属项目 values for now. If the report payload changes, add explicit dropdown key counts or selection logic first; do not reuse the fixed `Down` sequence silently.

Successful-run target:

- `run_daily_report_skill.py --stop-after blank-fill` should leave DingTalk on the write-log page.
- 明日工作计划 should show `整理 AXO 信息架构与构建 Roadmap`.
- Each row should show the expected date, content, hours, progress, 产品线=`其他`, and 所属项目=`非交付投入`.
- No submit action should occur.

If this flow fails, record the failing key/click in `last-run.jsonl`, then patch `fill_blank_write_log_keyboard.py`; do not revive the older scroll/dropdown coordinate path as the default unless the keyboard flow is proven impossible.

Latest real-run result:

- Table fields were correct: date, work item, hours, progress, 产品线=`其他`, and 所属项目=`非交付投入`.
- 明日工作计划 was blank with upfront coordinate clicks, including the follow-up `(1280,800)` attempt.
- Current production path uses the post-table path: final row 所属项目 -> Tab x3 -> paste 明日工作计划.
- Follow-up real runs verified post-table 明日工作计划 and both rows' 所属项目. The script parks the mouse at `(10,10)` before keyboard dropdown selection to prevent hover interference.

Date field warning from testing:

- Clicking the date field with Computer Use reliably opens the calendar.
- Picking the previous-month day by visible calendar coordinate is unsafe; one run intended `2026-06-30` but selected `2026-08-05`.
- `set_value` on the exposed/focused date text field can fail with "not settable".
- Computer Use `type_text` did not replace a selected date in one run.
- Clipboard paste with `dingtalk_keys.py paste 2026-06-30` did not replace the selected date; it left the wrong date selected.
- A trial click at `(604, 420)` in the open calendar did not navigate from `2026年 8月` to the previous month, so do not treat that point as the previous-month arrow.
- A trial click at `(579, 420)` in row 1's open calendar did navigate from `2026年 8月` to `2026年 7月`, and a second click at the same point navigated to `2026年 6月`.
- After row 1's calendar showed `2026年 6月`, clicking `(604, 557)` selected `2026-06-30`.
- In row 2's open calendar, clicking `(579, 486)` navigated from `2026年 7月` to `2026年 6月`; clicking `(604, 625)` selected `2026-06-30`.
- Do not continue the full workflow if the date is wrong. Stop, document the exact focused/selected state, and find a new date-entry strategy before filling other fields.

Content field warning from testing:

- After both row dates were corrected to `2026-06-30`, `set_value` on the visible row 1 work-item text area failed with `246 is an invalid element ID`.
- Treat DingTalk report table accessibility indexes as descriptive only. For work content, hours, progress, and dropdowns, use keyboard focus traversal plus clipboard paste.
- Historical fullscreen work-item coordinates that worked in testing:
  - Row 1 work item: click `(738, 292)`, then paste `梳理登录 alpha 1 信息架构与异常流程`.
  - Row 2 work item: click `(738, 347)`, then paste `整理下月 AI 工具费用申请明细`.
- Historical fullscreen hour coordinates that worked in testing:
  - Row 1 hour: click `(812, 292)`, type `6`.
  - Row 2 hour: click `(812, 347)`, type `2`.
- From row 2 hour, pressing Tab once moved focus to row 2 progress and horizontally scrolled the table to show 工时 / 进度 / 产品线. Type `100%`.
- Row 1 progress was then clickable at `(737, 293)` and accepted `80%`.
- From row 1 progress, pressing Tab once moved focus to row 1 产品线. Pressing Space opened the 产品线 dropdown; first item `其他` was at approximately `(813, 282)`.
- Row 2 产品线 opened by clicking approximately `(811, 346)`; first item `其他` remained at approximately `(813, 282)`.
- From row 2 产品线, pressing Tab once horizontally scrolled to 所属项目. The current focus landed in row 2 所属项目.
- 所属项目 dropdown second item `非交付投入` was at approximately `(684, 299)`. It worked for both row 2 after opening from focus, and row 1 after clicking row 1 所属项目 at approximately `(699, 296)`.
- Tomorrow plan field accepted clipboard paste after clicking approximately `(626, 455)`.
- Use `fill_table_keyboard_core.py` for the verified core table segment instead of manually repeating those clicks and keystrokes. It still uses a few focus-anchor clicks because DingTalk's iframe does not expose stable actionable cell IDs, but all value entry and horizontal movement are keyboard/clipboard driven.
- Pure keyboard dropdown selection is now handled by the default blank-draft keyboard flow. Keep the coordinate notes below as legacy fallback only.

## Stage 1: maximize and navigate

1. Let `scripts/run_daily_report_skill.py` call `scripts/maximize_dingtalk.py`.
2. Let the runner call `scripts/fullscreen_dingtalk.py` unless `--skip-fullscreen` is explicitly passed. This uses the Window menu first and falls back to Control+Command+F. If manual intervention is acceptable, the user-observed fallback is Control+Fn+F; AppleScript cannot reliably synthesize Fn.
3. Continue directly after the fullscreen command succeeds.
4. Let the runner call `scripts/open_write_log.py`.
5. Continue directly after `open_write_log.py` succeeds.

Current coordinate hints after maximize on a 2560x1440 display:

- 工作台: approximately `(18, 178)`.
- Pinned 日志: approximately `(423, 116)`.
- 写日志: the latest verified CGEvent logical point is around `(163, 139)`.

Treat these as hints from the latest observed layout, not absolute truth.

Historical issues:

- `maximize_dingtalk.py` previously failed when it required a named `钉钉` window. It now uses `window 1`.
- `maximize_dingtalk.py` also restores a missing DingTalk window via Window -> `打开DING窗口` when the process exists but no window is open.
- `open_write_log.py` previously reported success while the page stayed on messages because AppleScript `click at` missed the sidebar. It now defaults to the CGEvent driver.
- `open_write_log.py` can explicitly activate DingTalk when `DINGTALK_ALLOW_ACTIVATE=1` and then re-check frontmost state before each click. This fixed a run where Todoist became frontmost between reset and navigation; the script stopped rather than clicking the wrong app.
- Current native fullscreen CGEvent coordinate mapping is close to the logical center derived from the Retina screenshot. Use `screencapture` plus pixel detection when a visible button does not respond to a guessed coordinate.
- Verified native fullscreen navigation CGEvent points:
  - 工作台: script default `(9, 178)` with scale `(2, 2)` -> CG `(18, 356)` worked in the latest run.
  - Pinned 日志: observed point `(480, 113)` -> CG `(960, 226)` worked.
  - 写日志: `open_write_log.py` now detects the blue button from a Retina `screencapture`; the latest successful detected click was `(164, 140)`. Plain screenshot scaling `(176, 150)` and the window-offset guess `(160, 168)` missed the button in some states.
- If navigation reaches the log list but not the write page, update `open_write_log.py` coordinates instead of finishing the navigation manually.

## Legacy visible-column flow

The sections below describe the older staged coordinate/scroll flow. Keep them as fallback/calibration references only. The default runner now uses `fill_blank_write_log_keyboard.py` unless `--legacy-visible-flow` is passed.

## Legacy Stage 2: add rows

Use the Add button until the row count matches the summarized report items. On the clean blank write-log page, the verified Add sequence for two rows was:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/ensure_table_rows.py --rows 2
```

Current clean-layout Add coordinates:

- First add: `(1034, 706)`.
- Second add after the first row appears: `(1034, 633)`.

Do not reuse old Add coordinate `(552, 378)`; it clicked the wrong place on the clean blank page.

## Legacy Stage 3: date and work content

Preferred script:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/fill_visible_rows.py \
  --date 2026-06-30 \
  --rows '[{"content":"梳理登录 alpha 1 信息架构与异常流程"},{"content":"整理下月 AI 工具费用申请明细"}]'
```

For newly added blank rows, do not use `--replace-existing`; page-level selection can happen if the field focus is not actually inside the input.

Manual equivalent for each row:

1. Click the date cell.
2. Type `yyyy-mm-dd`.
3. Click the work-content cell to blur the date field. Do not press Enter.
4. Paste Chinese text with `dingtalk_keys.py paste "...text..."`.

Observed row coordinate hints:

- Row 1 date: around `(1186, 554)`.
- Row 2 date: around `(1186, 647)`.
- Row 1 work content: around `(1386, 554)`.
- Row 2 work content: around `(1386, 647)`.

Latest centered write-log layout after maximize placed cells closer to:

- Row 1 date: around `(580, 303)`.
- Row 2 date: around `(580, 354)`.
- Row 1 work content: around `(690, 303)`.
- Row 2 work content: around `(690, 354)`.

Old retained-draft fullscreen coordinates below are deprecated because they came from a pre-filled draft, not a clean blank page:

- Row 1 date: around `(622, 394)`.
- Row 2 date: around `(622, 459)`.
- Row 1 work content: around `(759, 394)`.
- Row 2 work content: around `(759, 459)`.
- Row 1 visible hours cell: around `(856, 394)`.
- Row 2 visible hours cell: around `(856, 459)`.

Verified fullscreen date-picker coordinates for `2026-06-30` from the current layout:

- Row 1 date field: click around `(617, 395)` to open.
- Row 1 previous-month arrow: `(579, 420)`.
- Row 1 June 30 date cell: `(604, 557)`.
- Row 2 date field: click around `(617, 461)` to open.
- Row 2 previous-month arrow: `(579, 486)`.
- Row 2 June 30 date cell: `(604, 625)`.

The fullscreen page may still hide progress, product line, and project columns to the right. After filling visible cells, use horizontal scrolling before running the next script.

Current clean-layout verified sequence:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/fill_visible_rows.py \
  --date 2026-06-30 \
  --rows '[{"content":"梳理登录 alpha 1 信息架构与异常流程"},{"content":"整理下月 AI 工具费用申请明细"}]'

python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/fill_visible_hours.py \
  --rows '[{"hours":6},{"hours":2}]'
```

Verified clean-layout hour coordinates:

- Row 1 hours: `(1518, 554)`.
- Row 2 hours: `(1518, 647)`.

## Legacy Stage 4: hours and progress

After visible columns are filled, prefer horizontal CGEvent scrolling over blind Tab traversal to move through the table until 工时, 进度, 产品线, and 所属项目 are visible. Fill values with keyboard and clipboard input:

1. Focus the table cell nearest the current row.
2. Press Tab until 工时 is active.
3. Type or paste the hours value.
4. Press Tab.
5. Type or paste the progress percentage exactly from the daily report, such as `70%` or `80%`.
6. Continue only if the scripted stage returns success.

Progress values are per-row data. Never default all rows to `100%`.

Deprecated fullscreen path after filling work items:

1. Click row 1 hour around `(812, 292)`, type `6`.
2. Click row 2 hour around `(812, 347)`, type `2`.
3. Press Tab once from row 2 hour. The table scrolls horizontally and focuses row 2 progress.
4. Type `100%`.
5. Click row 1 progress around `(737, 293)`, type `80%`.

Do not rely on that Tab path. A later run typed `100%` into 明日工作计划, proving focus had escaped the table. The safer path is:

1. Fill the left-side visible fields and 工时.
2. Use `dingtalk_scroll.py --horizontal -450` at the table center to expose 进度 / 产品线.
3. Fill visible progress fields by coordinate or keyboard focus. Clean-layout progress coordinates are row 1 `(1336, 554)`, row 2 `(1336, 647)`.
4. Use `dingtalk_scroll.py --horizontal -900` or another right scroll to expose 所属项目.

Preferred script for the verified keyboard core:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/fill_table_keyboard_core.py \
  --left-only \
  --rows '[{"content":"梳理登录 alpha 1 信息架构与异常流程","hours":6,"progress":"80%"},{"content":"整理下月 AI 工具费用申请明细","hours":2,"progress":"100%"}]'
```

After running it, scroll horizontally to expose progress/product columns. Do not use the legacy progress Tab path unless it is revalidated.

When 工时 and 进度 are visible at the current coordinate hints, use:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/fill_hours_progress.py \
  --rows '[{"hours":6,"progress":"80%"},{"hours":2,"progress":"100%"}]'
```

## Legacy Stage 5: dropdowns

Use keyboard where possible. The coordinate dropdown notes below are legacy fallback references:

1. Move focus to 产品线.
2. Press Space to open the dropdown.
3. Choose the first item, `其它`.
4. Move focus to 所属项目.
5. Open the dropdown.
6. Choose the second item, `非交付投入`.

If keyboard selection is unreliable, localize the failure and update the script. Latest observed menu first item appeared around `(833, 288)` after opening 产品线.

Current verified fullscreen dropdown path:

1. Press Tab once from row 1 progress to focus row 1 产品线.
2. Press Space, then click the first item `其他` around `(813, 282)`.
3. Click row 2 产品线 around `(811, 346)`, then click the first item `其他` around `(813, 282)`.
4. Press Tab once from row 2 产品线 to scroll to 所属项目 and focus row 2 所属项目.
5. Press Space, then click the second item `非交付投入` around `(684, 299)`.
6. Click row 1 所属项目 around `(699, 296)`, then click the second item `非交付投入` around `(684, 299)`.

Keyboard dropdown test target:

1. Focus an already-correct dropdown value in a draft.
2. Open it with Space.
3. Try selecting the same value with arrows or typeahead.
4. Confirm the value stayed correct during a dedicated manual or scripted test before documenting it as production-safe.

When coordinate hints still match, use:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/fill_dropdowns.py --rows 2
```

Defaults are 产品线 item 1 (`其它`) and 所属项目 item 2 (`非交付投入`). Override `--product-item` or `--project-item` only when DingTalk menu ordering changes.

## Legacy Stage 6: tomorrow plan and final check

Paste 明日工作计划 from the generated report summary:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/fill_tomorrow_plan.py "整理 AXO 信息架构与构建 Roadmap"
```

If focus is not already in the plan field, provide `--x` and `--y` from the maintained coordinate hints. Leave the page open for manual review. Do not submit.

After filling the draft, exit native fullscreen but keep the write-log page open:

```bash
python3 /Users/wally/.codex/skills/dingtalk-daily-report-automation/scripts/fullscreen_dingtalk.py --action exit
```

This command uses the Window menu's Exit Full Screen item only. It should report `already-not-fullscreen` rather than toggling into fullscreen when DingTalk is already windowed.

## Script granularity

The preferred sequence is encoded in `run_daily_report_skill.py`. If running scripts manually, use this sequence for fast but debuggable execution:

1. `maximize_dingtalk.py`
2. Optional: `fullscreen_dingtalk.py`
3. `open_write_log.py`
4. `fill_blank_write_log_keyboard.py`
5. `fullscreen_dingtalk.py --action exit`

## Fallback Recording

When Computer Use is used for failure localization or an explicitly requested visual check, record:

- Failing stage name from `last-run.jsonl`.
- What the script attempted.
- Why the script was insufficient.
- The exact next script target, such as "replace navigation coordinate click with keyboard app search" or "implement dropdown keyboard typeahead".

Do not update the skill to claim a new or changed step is script-safe until a later run completes it without Computer Use execution.

## Recovery notes

- If focus is unclear, click a known cell and restart the local Tab sequence from that point.
- If date entry opens a calendar, select all and type the `yyyy-mm-dd` string, then press Enter.
- If DingTalk refreshes or loading overlays appear, wait before continuing.
- If a dropdown selection causes horizontal scroll or focus movement, restart from a known focus anchor before filling the next field.
