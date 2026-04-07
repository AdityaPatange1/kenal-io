#!/usr/bin/env bash
# Run all kenal-io examples sequentially (colored output via Python runner).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec "${PYTHON:-python3}" -u "$ROOT/scripts/run_examples.py" "$@"
