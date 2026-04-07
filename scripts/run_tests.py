#!/usr/bin/env python3
"""Run the test suite with pytest; colored output and clear section banners."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import console as C  # noqa: E402


def main() -> int:
    os.chdir(ROOT)

    pytest_exe = shutil.which("pytest")
    if pytest_exe:
        cmd = [pytest_exe, "tests/", "-v", "--tb=short", "--color=yes"]
    else:
        cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "--color=yes"]

    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(ROOT / "src"))
    # Help pytest and plugins emit ANSI when stdout is piped or non-tty runners.
    env.setdefault("PY_COLORS", "1")
    env.setdefault("FORCE_COLOR", "1")

    C.section("kenal-io — test suite")
    C.log_line("●", f"Root: {ROOT}", color=C.C.BRIGHT_BLUE)
    C.log_line("●", f"Command: {' '.join(cmd)}", color=C.C.BRIGHT_BLUE)
    print()
    sys.stdout.flush()

    result = subprocess.run(cmd, cwd=ROOT, env=env)
    code = result.returncode

    print()
    C.section("Test summary")
    if code == 0:
        C.success_banner("pytest exited cleanly.")
    else:
        C.failure_banner(f"pytest exited with code {code}.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
