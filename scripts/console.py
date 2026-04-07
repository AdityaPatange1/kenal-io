"""ANSI colors and pretty-print helpers for kenal runner scripts."""

from __future__ import annotations

import os
import shutil
import sys
from typing import TextIO


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[97m"

    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


def term_width(default: int = 80) -> int:
    w = shutil.get_terminal_size(fallback=(default, 24)).columns
    return max(40, w)


def supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


_NO_COLOR = not supports_color()


def _c(code: str, text: str) -> str:
    if _NO_COLOR:
        return text
    return f"{code}{text}{C.RESET}"


def bold(text: str) -> str:
    return _c(C.BOLD, text)


def dim(text: str) -> str:
    return _c(C.DIM, text)


def ok(text: str) -> str:
    return _c(C.BRIGHT_GREEN, text)


def warn(text: str) -> str:
    return _c(C.BRIGHT_YELLOW, text)


def err(text: str) -> str:
    return _c(C.BRIGHT_RED, text)


def info(text: str) -> str:
    return _c(C.BRIGHT_CYAN, text)


def label(text: str) -> str:
    return _c(C.BRIGHT_MAGENTA, text)


def section(title: str, *, stream: TextIO = sys.stdout) -> None:
    print(file=stream)
    rule(stream=stream)
    print(bold(info(f"  {title}")), file=stream)
    rule(stream=stream)


def banner(text: str, *, stream: TextIO = sys.stdout) -> None:
    print(bold(info(f"▶ {text}")), file=stream)


def rule(*, char: str = "─", stream: TextIO = sys.stdout) -> None:
    w = term_width()
    print(dim(char * min(w, 100)), file=stream)


def log_line(prefix: str, message: str, *, color: str = C.BRIGHT_BLUE, stream: TextIO = sys.stdout) -> None:
    if _NO_COLOR:
        print(f"{prefix} {message}", file=stream)
    else:
        print(f"{color}{prefix}{C.RESET} {message}", file=stream)


def print_kv(key: str, value: object, *, stream: TextIO = sys.stdout) -> None:
    print(f"  {label(key + ':')} {value}", file=stream)


def success_banner(message: str, *, stream: TextIO = sys.stdout) -> None:
    print(ok(f"✓ {message}"), file=stream)


def failure_banner(message: str, *, stream: TextIO = sys.stdout) -> None:
    print(err(f"✗ {message}"), file=stream)


def muted(text: str) -> str:
    return dim(text)
