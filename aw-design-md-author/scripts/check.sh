#!/usr/bin/env bash
# Usage: check.sh DESIGN.md [DESIGN.prev.md] [--annotation]
# Exit 0 = checked gates pass, 1 = content/protection failure, 2 = unavailable.
# Requires Python 3 + PyYAML and npx (or an explicit DESIGN_MD_CLI executable).
set -uo pipefail
command -v python3 >/dev/null 2>&1 || { echo 'Python 3 unavailable' >&2; exit 2; }
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/check.py" "$@"
