"""Behavioral checks for bmad-method-refactorskills-convert-reviewpr-and-auditfileref (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bmad-method")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-audit-file-refs/SKILL.md')
    assert 'description: Audit BMAD source files for file-reference convention violations using parallel Haiku subagents. Use when checking path references in workflow and task files.' in text, "expected to find: " + 'description: Audit BMAD source files for file-reference convention violations using parallel Haiku subagents. Use when checking path references in workflow and task files.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-audit-file-refs/SKILL.md')
    assert 'Read `prompts/instructions.md` and execute.' in text, "expected to find: " + 'Read `prompts/instructions.md` and execute.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-audit-file-refs/SKILL.md')
    assert 'disable-model-invocation: true' in text, "expected to find: " + 'disable-model-invocation: true'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-audit-file-refs/prompts/instructions.md')
    assert '.claude/skills/bmad-os-audit-file-refs/prompts/instructions.md' in text, "expected to find: " + '.claude/skills/bmad-os-audit-file-refs/prompts/instructions.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-review-pr/README.md')
    assert 'See `prompts/instructions.md` for full prompt structure, severity ratings, and sandboxing rules.' in text, "expected to find: " + 'See `prompts/instructions.md` for full prompt structure, severity ratings, and sandboxing rules.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-review-pr/README.md')
    assert 'Use `/bmad-os-review-pr` to review a specific PR:' in text, "expected to find: " + 'Use `/bmad-os-review-pr` to review a specific PR:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-review-pr/README.md')
    assert '> "Use /bmad-os-review-pr to review PR #123"' in text, "expected to find: " + '> "Use /bmad-os-review-pr to review PR #123"'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-review-pr/SKILL.md')
    assert "description: Adversarial PR review tool (Raven's Verdict). Cynical deep review transformed into professional engineering findings. Use when asked to review a PR." in text, "expected to find: " + "description: Adversarial PR review tool (Raven's Verdict). Cynical deep review transformed into professional engineering findings. Use when asked to review a PR."[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-review-pr/SKILL.md')
    assert 'Read `prompts/instructions.md` and execute.' in text, "expected to find: " + 'Read `prompts/instructions.md` and execute.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-review-pr/SKILL.md')
    assert 'disable-model-invocation: true' in text, "expected to find: " + 'disable-model-invocation: true'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-review-pr/prompts/instructions.md')
    assert '## CRITICAL: Sandboxed Execution Rules' in text, "expected to find: " + '## CRITICAL: Sandboxed Execution Rules'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-review-pr/prompts/instructions.md')
    assert '## Tone Transformation' in text, "expected to find: " + '## Tone Transformation'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bmad-os-review-pr/prompts/instructions.md')
    assert '## Adversarial Review' in text, "expected to find: " + '## Adversarial Review'[:80]

