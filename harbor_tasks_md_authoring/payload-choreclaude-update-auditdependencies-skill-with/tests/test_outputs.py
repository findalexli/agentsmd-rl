"""Behavioral checks for payload-choreclaude-update-auditdependencies-skill-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/payload")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audit-dependencies/SKILL.md')
    assert "- If the same vulnerable package appears through many transitive paths, a global override may be needed. Be careful that it doesn't affect unrelated consumers on a different major version — use parent" in text, "expected to find: " + "- If the same vulnerable package appears through many transitive paths, a global override may be needed. Be careful that it doesn't affect unrelated consumers on a different major version — use parent"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audit-dependencies/SKILL.md')
    assert 'Fix dependency vulnerabilities reported by `.github/workflows/audit-dependencies.sh`. Prefer fixes in this order: direct dependency bump > lockfile update > pnpm override. Every override requires just' in text, "expected to find: " + 'Fix dependency vulnerabilities reported by `.github/workflows/audit-dependencies.sh`. Prefer fixes in this order: direct dependency bump > lockfile update > pnpm override. Every override requires just'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audit-dependencies/SKILL.md')
    assert 'Before applying fixes, present a summary table to the user showing each vulnerability, the proposed fix strategy (direct bump / lockfile update / override), and justification. Get confirmation before ' in text, "expected to find: " + 'Before applying fixes, present a summary table to the user showing each vulnerability, the proposed fix strategy (direct bump / lockfile update / override), and justification. Get confirmation before '[:80]

