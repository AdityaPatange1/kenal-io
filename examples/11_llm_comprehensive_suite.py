"""Comprehensive Ollama-backed LLM suite (~50 scenarios).

This is an *example* you can run to sanity-check reliability of LLM execution
paths across the kenal primitives: Block / Plate / Road / Frame and direct engine
calls.

By default:
  - If Ollama is unreachable, this script exits 0 (skipped) with a clear message.
  - Set KENAL_REQUIRE_LLM=1 to fail when Ollama is down.

Reliability controls:
  - KENAL_LLM_RETRIES: integer, default 1. Retries each case on failure.
  - KENAL_LLM_STRICT: if set to 1/true/yes, any failed case exits 1.
  - KENAL_LLM_MAX_FAILS: allow up to N failures before failing (default 0 in strict mode,
    default 5 in non-strict mode).
"""

from __future__ import annotations

import os
import re
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from llm_support import banner, should_skip_llm_example  # noqa: E402

from kenal import Block, Frame, Plate, Road  # noqa: E402
from kenal.engine import generate  # noqa: E402


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").lower() in ("1", "true", "yes", "y", "on")


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _color(s: str, code: str) -> str:
    if os.environ.get("NO_COLOR"):
        return s
    return f"\033[{code}m{s}\033[0m"


def green(s: str) -> str:
    return _color(s, "92")


def red(s: str) -> str:
    return _color(s, "91")


def yellow(s: str) -> str:
    return _color(s, "93")


def cyan(s: str) -> str:
    return _color(s, "96")


def dim(s: str) -> str:
    return _color(s, "2")


Validator = Callable[[str], bool]
Runner = Callable[[], str]


@dataclass(frozen=True, slots=True)
class Case:
    name: str
    run: Runner
    validate: Validator
    hint: str = ""


def _one_word_case(expected: str) -> Validator:
    e = expected.strip().lower()

    def _v(text: str) -> bool:
        t = text.strip().lower()
        return t == e

    return _v


def _contains(substr: str) -> Validator:
    s = substr.lower()

    def _v(text: str) -> bool:
        return s in text.lower()

    return _v


def _regex(pattern: str) -> Validator:
    rx = re.compile(pattern, re.IGNORECASE)

    def _v(text: str) -> bool:
        return rx.search(text) is not None

    return _v


def _safe_preview(text: str, limit: int = 160) -> str:
    t = " ".join(text.replace("\n", " ").split())
    return t if len(t) <= limit else t[: limit - 1] + "…"


def _mk_block(name: str, rules: list[str]) -> Block:
    return Block(name=name, rules=rules)


def _run_block(block: Block, prompt: str) -> str:
    out = block.run(prompt).output
    return out if isinstance(out, str) else str(out)


def _run_road(stops: list[Block | Plate], prompt: str) -> str:
    road = Road(name="r", stops=stops)
    results = road.run(prompt)
    last = results[-1].output
    return last if isinstance(last, str) else str(last)


def _run_frame(roads: list[Road], prompt: str) -> str:
    frame = Frame(name="f", roads=roads)
    results = frame.run(prompt)
    last = results[-1].output
    return last if isinstance(last, str) else str(last)


def build_cases() -> list[Case]:
    cases: list[Case] = []

    # 1-15: direct engine.generate with strict single-token outputs.
    tokens = [
        ("PONG", "Reply with exactly: PONG"),
        ("ALPHA", "Reply with exactly: ALPHA"),
        ("BRAVO", "Reply with exactly: BRAVO"),
        ("CHARLIE", "Reply with exactly: CHARLIE"),
        ("DELTA", "Reply with exactly: DELTA"),
        ("ECHO", "Reply with exactly: ECHO"),
        ("FOXTROT", "Reply with exactly: FOXTROT"),
        ("GOLF", "Reply with exactly: GOLF"),
        ("HOTEL", "Reply with exactly: HOTEL"),
        ("INDIA", "Reply with exactly: INDIA"),
        ("JULIET", "Reply with exactly: JULIET"),
        ("KILO", "Reply with exactly: KILO"),
        ("LIMA", "Reply with exactly: LIMA"),
        ("MIKE", "Reply with exactly: MIKE"),
        ("NOVEMBER", "Reply with exactly: NOVEMBER"),
    ]
    for tok, instr in tokens:
        cases.append(
            Case(
                name=f"engine.generate exact token: {tok}",
                run=lambda tok=tok, instr=instr: generate(system=instr, prompt="go"),
                validate=_one_word_case(tok),
                hint=(
                    "If this fails consistently, Ollama/chat may be misconfigured or a tool is "
                    "interfering."
                ),
            )
        )

    # Extra engine.generate exact-token cases (to ensure >= 50 total).
    more_tokens = [
        ("OSCAR", "Reply with exactly: OSCAR"),
        ("PAPA", "Reply with exactly: PAPA"),
        ("QUEBEC", "Reply with exactly: QUEBEC"),
        ("ROMEO", "Reply with exactly: ROMEO"),
        ("SIERRA", "Reply with exactly: SIERRA"),
        ("TANGO", "Reply with exactly: TANGO"),
        ("UNIFORM", "Reply with exactly: UNIFORM"),
        ("VICTOR", "Reply with exactly: VICTOR"),
        ("WHISKEY", "Reply with exactly: WHISKEY"),
        ("XRAY", "Reply with exactly: XRAY"),
        ("YANKEE", "Reply with exactly: YANKEE"),
        ("ZULU", "Reply with exactly: ZULU"),
    ]
    for tok, instr in more_tokens:
        cases.append(
            Case(
                name=f"engine.generate exact token: {tok}",
                run=lambda tok=tok, instr=instr: generate(system=instr, prompt="go"),
                validate=_one_word_case(tok),
            )
        )

    # 16-30: single Block LLM path with crisp constraints.
    block_specs = [
        ("b_yes", ["Reply with exactly one word: YES"], "anything", _one_word_case("YES")),
        ("b_no", ["Reply with exactly one word: NO"], "anything", _one_word_case("NO")),
        ("b_42", ["Reply with exactly one token: 42"], "number please", _one_word_case("42")),
        ("b_ok", ["Reply with exactly: OK"], "ack", _one_word_case("OK")),
        ("b_red", ["Reply with exactly one word: RED"], "color", _one_word_case("RED")),
        ("b_blue", ["Reply with exactly one word: BLUE"], "color", _one_word_case("BLUE")),
        ("b_cat", ["Reply with exactly one word: CAT"], "animal", _one_word_case("CAT")),
        ("b_dog", ["Reply with exactly one word: DOG"], "animal", _one_word_case("DOG")),
        ("b_true", ["Reply with exactly one word: TRUE"], "bool", _one_word_case("TRUE")),
        ("b_false", ["Reply with exactly one word: FALSE"], "bool", _one_word_case("FALSE")),
        ("b_a", ["Reply with exactly one character: A"], "letter", _one_word_case("A")),
        ("b_z", ["Reply with exactly one character: Z"], "letter", _one_word_case("Z")),
        ("b_ping", ["Reply with exactly: PING"], "pong?", _one_word_case("PING")),
        ("b_pong", ["Reply with exactly: PONG"], "ping?", _one_word_case("PONG")),
        ("b_hello", ["Reply with exactly: HELLO"], "hi", _one_word_case("HELLO")),
    ]
    for name, rules, prompt, validator in block_specs:
        cases.append(
            Case(
                name=f"Block exact output: {name}",
                run=lambda name=name, rules=rules, prompt=prompt: _run_block(
                    _mk_block(name, rules), prompt
                ),
                validate=validator,
            )
        )

    # 31-40: Road / Frame sequencing.
    cases.append(
        Case(
            name="Road two-block sequence (ALPHA -> BRAVO)",
            run=lambda: _run_road(
                [
                    _mk_block("a", ["Reply with exactly: ALPHA"]),
                    _mk_block("b", ["Reply with exactly: BRAVO"]),
                ],
                "seed",
            ),
            validate=_one_word_case("BRAVO"),
        )
    )
    cases.append(
        Case(
            name="Frame with one Road (final token NOVEMBER)",
            run=lambda: _run_frame(
                [
                    Road(
                        name="main",
                        stops=[
                            _mk_block("x", ["Reply with exactly: MIKE"]),
                            _mk_block("y", ["Reply with exactly: NOVEMBER"]),
                        ],
                    )
                ],
                "seed",
            ),
            validate=_one_word_case("NOVEMBER"),
        )
    )

    # Plate fan-out as a stop: last block output should be forwarded.
    def _plate_stop() -> str:
        plate = Plate(
            name="p",
            blocks=[
                _mk_block("p1", ["Reply with exactly: ALPHA"]),
                _mk_block("p2", ["Reply with exactly: BRAVO"]),
                _mk_block("p3", ["Reply with exactly: CHARLIE"]),
            ],
            rules=["Reply with only the required token."],
        )
        return _run_road([plate, _mk_block("after", ["Reply with exactly: DELTA"])], "seed")

    cases.append(
        Case(
            name="Road with Plate stop + final Block",
            run=_plate_stop,
            validate=_one_word_case("DELTA"),
        )
    )

    # 41-50: format/structure prompts (still deterministic-ish).
    cases.append(
        Case(
            name="JSON object output (keys: ok, n)",
            run=lambda: _run_block(
                _mk_block(
                    "json",
                    [
                        "Reply with a single-line JSON object only.",
                        "It MUST have keys ok and n.",
                        "ok must be true, n must be 1.",
                    ],
                ),
                "return json",
            ),
            validate=_regex(r"^\s*\{\s*\"ok\"\s*:\s*true\s*,\s*\"n\"\s*:\s*1\s*\}\s*$"),
            hint=(
                "Model may add whitespace; regex allows whitespace but expects exact keys and "
                "values."
            ),
        )
    )
    cases.append(
        Case(
            name="CSV one-line output",
            run=lambda: _run_block(
                _mk_block(
                    "csv",
                    [
                        "Reply with exactly one line of CSV only.",
                        "The line MUST be: a,b,c",
                    ],
                ),
                "csv",
            ),
            validate=_one_word_case("a,b,c"),
        )
    )
    cases.append(
        Case(
            name="Lowercase token only",
            run=lambda: _run_block(
                _mk_block(
                    "lower",
                    [
                        "Reply with exactly: ok",
                        "Use lowercase letters only.",
                    ],
                ),
                "ack",
            ),
            validate=_one_word_case("ok"),
        )
    )
    cases.append(
        Case(
            name="No punctuation token",
            run=lambda: _run_block(
                _mk_block(
                    "nopunct",
                    [
                        "Reply with exactly one word: HELLO",
                        "Do not include punctuation.",
                    ],
                ),
                "hello",
            ),
            validate=_one_word_case("hello"),
        )
    )
    cases.append(
        Case(
            name="Language control (French token OUI)",
            run=lambda: _run_block(
                _mk_block(
                    "fr",
                    [
                        "Reply with exactly one word in French: OUI",
                        "Output must be uppercase.",
                    ],
                ),
                "yes?",
            ),
            validate=_one_word_case("OUI"),
        )
    )

    # Ensure we have ~50 cases.
    assert len(cases) >= 50
    return cases[:50]


def main() -> None:
    if should_skip_llm_example():
        return

    retries = max(1, _env_int("KENAL_LLM_RETRIES", 1))
    strict = _env_truthy("KENAL_LLM_STRICT")
    max_fails = _env_int("KENAL_LLM_MAX_FAILS", 0 if strict else 5)

    banner("LLM Comprehensive Suite (~50 cases)")
    print(f"  retries: {retries}")
    print(f"  strict:  {strict}")
    print(f"  max_fails allowed: {max_fails}")
    print()

    cases = build_cases()
    start = time.time()

    passed = 0
    failed = 0
    failures: list[str] = []

    for idx, case in enumerate(cases, start=1):
        prefix = f"[{idx:02d}/{len(cases):02d}]"
        print(cyan(f"{prefix} {case.name}"))
        ok = False
        last_out = ""
        last_err: str | None = None
        for attempt in range(1, retries + 1):
            try:
                out = case.run()
                last_out = out
                ok = case.validate(out)
                if ok:
                    break
                last_err = "validation failed"
            except Exception as exc:  # example harness
                last_err = str(exc)
                last_out = ""
            if attempt < retries:
                print(dim(f"  retrying ({attempt}/{retries})…"))

        if ok:
            passed += 1
            print("  " + green("PASS") + f"  {dim(_safe_preview(last_out))}")
        else:
            failed += 1
            failures.append(case.name)
            print("  " + red("FAIL") + f"  {dim(_safe_preview(last_out))}")
            if last_err:
                print("  " + yellow("reason") + f": {last_err}")
            if case.hint:
                print("  " + yellow("hint") + f": {case.hint}")
        print()

        if failed > max_fails:
            print(red(f"Too many failures ({failed} > {max_fails}). Stopping early."))
            break

    dur = time.time() - start
    print(dim("─" * 72))
    print(f"  total:  {len(cases)}")
    print(green(f"  passed: {passed}"))
    print(red(f"  failed: {failed}"))
    print(f"  time:   {dur:.2f}s")
    if failures:
        print()
        print(yellow("  failed cases:"))
        for name in failures[:20]:
            print(f"    - {name}")
        if len(failures) > 20:
            print(f"    - … {len(failures) - 20} more")
    print()

    if strict and failed > 0:
        raise SystemExit(1)
    if failed > max_fails:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
