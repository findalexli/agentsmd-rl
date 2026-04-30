"""Behavioral checks for agent-rules-skill-fix-add-exact-name-matching (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-rules-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agents/SKILL.md')
    assert '| `CowriterAjaxController.php` | `AjaxController.php` | **WRONG** - name mismatch |' in text, "expected to find: " + '| `CowriterAjaxController.php` | `AjaxController.php` | **WRONG** - name mismatch |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agents/SKILL.md')
    assert '| **Numeric values** | PHPStan level, coverage %, etc. from actual configs |' in text, "expected to find: " + '| **Numeric values** | PHPStan level, coverage %, etc. from actual configs |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agents/SKILL.md')
    assert 'make -n test-mutation 2>/dev/null && echo "EXISTS" || echo "MISSING"' in text, "expected to find: " + 'make -n test-mutation 2>/dev/null && echo "EXISTS" || echo "MISSING"'[:80]

