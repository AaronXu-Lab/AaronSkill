#!/usr/bin/env bash
# check.sh — Spec-compliance gate for iterating a DESIGN.md.
#
# Usage:
#   scripts/check.sh DESIGN.md                # lint only
#   scripts/check.sh DESIGN.md DESIGN.prev.md # lint + regression diff vs a baseline
#
# Exit codes:
#   0 = lint clean (and, if a baseline was given, no regression)
#   1 = lint reported errors, OR diff reported a regression
#   2 = usage / environment problem
#
# Requires network access to npm (uses `npx @google/design.md`). If unavailable,
# fall back to the manual checklist in references/lint-rules.md.

set -uo pipefail

CUR="${1:-}"
PREV="${2:-}"

if [ -z "$CUR" ]; then
  echo "usage: check.sh DESIGN.md [DESIGN.prev.md]" >&2
  exit 2
fi
if [ ! -f "$CUR" ]; then
  echo "file not found: $CUR" >&2
  exit 2
fi

DM="npx --yes @google/design.md"
fail=0

echo "== lint: $CUR =="
if $DM lint "$CUR"; then
  echo "  lint: structural validation passed (exit 0)"
else
  echo "  lint: ERRORS found (exit 1)" >&2
  fail=1
fi

if [ -n "$PREV" ]; then
  if [ ! -f "$PREV" ]; then
    echo "baseline not found: $PREV" >&2
    exit 2
  fi
  echo
  echo "== diff (regression check): $PREV -> $CUR =="
  if $DM diff "$PREV" "$CUR"; then
    echo "  diff: no regression (exit 0)"
  else
    echo "  diff: REGRESSION detected (exit 1)" >&2
    fail=1
  fi
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "RESULT: PASS — DESIGN.md structural checks passed."
  echo "NOTE: Any code-backed components or alternate themes still require their owning visual, contrast, and accessibility checks."
else
  echo "RESULT: FAIL — fix the issues above before declaring the iteration done." >&2
fi
exit "$fail"
