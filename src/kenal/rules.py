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

    def __str__(self) -> str:
        prefix = "[MUST]" if self.enforce else "[SHOULD]"
        return f"{prefix} {self.text}"


def normalize_rules(raw: list[str | Rule] | None) -> list[Rule]:
    """Convert a mixed list of strings and Rule objects into a uniform list."""
    if not raw:
        return []
    return [Rule(text=r) if isinstance(r, str) else r for r in raw]


def compile_rules(rules: list[Rule]) -> str:
    """Compile a list of rules into a prompt-ready instruction block."""
    if not rules:
        return ""
    lines = ["You MUST follow these rules when processing the input:"]
    for idx, rule in enumerate(rules, 1):
        lines.append(f"  {idx}. {rule}")
    return "\n".join(lines)
