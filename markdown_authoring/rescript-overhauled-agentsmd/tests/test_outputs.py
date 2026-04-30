"""Behavioral checks for rescript-overhauled-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rescript")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Use underscore patterns carefully** - Don't use `_` patterns as lazy placeholders for new language features that then get forgotten. Only use them when you're certain the value should be ignored f" in text, "expected to find: " + "- **Use underscore patterns carefully** - Don't use `_` patterns as lazy placeholders for new language features that then get forgotten. Only use them when you're certain the value should be ignored f"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Never modify `parsetree0.ml`** - Existing PPX (parser extensions) rely on this frozen v0 version. When changing `parsetree.ml`, always update the mapping modules `ast_mapper_from0.ml` and `ast_map' in text, "expected to find: " + '- **Never modify `parsetree0.ml`** - Existing PPX (parser extensions) rely on this frozen v0 version. When changing `parsetree.ml`, always update the mapping modules `ast_mapper_from0.ml` and `ast_map'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Be careful with similar constructor names across different IRs** - Note that `Lam` (Lambda IR) and `Lambda` (typed lambda) have variants with similar constructor names like `Ltrywith`, but they re' in text, "expected to find: " + '- **Be careful with similar constructor names across different IRs** - Note that `Lam` (Lambda IR) and `Lambda` (typed lambda) have variants with similar constructor names like `Ltrywith`, but they re'[:80]

