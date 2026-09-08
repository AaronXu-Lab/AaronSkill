#!/usr/bin/env sh
# All-or-nothing artifact checks. Text reports still need the semantic rubric.
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$SCRIPT_DIR/check_required.py"
