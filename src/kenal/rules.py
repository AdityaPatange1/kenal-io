"""Natural-language runtime rules for kenal components."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rule:
    """A natural-language runtime rule.

    Rules are expressed in plain English and compiled into system-level
    instructions that govern how a Block processes its input.

    Args:
        text: The rule expressed in natural language.
        enforce: If ``True`` the rule is mandatory (MUST); otherwise advisory (SHOULD).
    """

    text: str
    enforce: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError(f"Rule.text must be str, got {type(self.text).__name__}")
        if not self.text.strip():
            raise ValueError("Rule.text cannot be empty")

    def __str__(self) -> str:
        prefix = "[MUST]" if self.enforce else "[SHOULD]"
        return f"{prefix} {self.text}"


def normalize_rules(raw: list[str | Rule] | None) -> list[Rule]:
    """Convert a mixed list of strings and Rule objects into a uniform list."""
    normalized: list[Rule] = []

    if raw is None or len(raw) == 0:
        return normalized

    for r in raw:
        if isinstance(r, Rule):
            normalized.append(r)
        elif isinstance(r, str):
            normalized.append(Rule(text=r))
        else:
            raise TypeError(f"Each rule must be a str or Rule, got {type(r).__name__}")

    return normalized


def compile_rules(rules: list[Rule]) -> str:
    """Compile a list of rules into a prompt-ready instruction block."""
    if not rules:
        return ""

    lines = ["You MUST follow these rules when processing the input:"]
    for idx, rule in enumerate(rules, 1):
        lines.append(f"  {idx}. {rule}")

    return "\n".join(lines)
