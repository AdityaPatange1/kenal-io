"""Example: natural-language rules and compile_rules for prompts."""

from __future__ import annotations

from kenal.rules import Rule, compile_rules, normalize_rules


def main() -> None:
    print()
    raw = [
        "Answer in clear, short sentences.",
        Rule(text="Prefer bullet lists when listing items.", enforce=False),
    ]
    rules = normalize_rules(raw)
    compiled = compile_rules(rules)
    print("  Normalized rules:")
    for r in rules:
        print(f"    - {r}")
    print()
    print("  Compiled block (for LLM system prompt):")
    for line in compiled.splitlines():
        print(f"    {line}")
    print()


if __name__ == "__main__":
    main()
