#!/bin/bash

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)" || exit 1

python3 "$SCRIPT_DIR/link-skills.py" "$@"
result=$?

printf '\n按回车键关闭窗口…'
read -r
exit "$result"
