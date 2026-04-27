"""Behavioral checks for agentops-fix-add-standards-dependency-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentops")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core-kit/skills/crank/SKILL.md')
    assert 'When `/crank` is invoked without an epic-id, check the preceding conversation for context:' in text, "expected to find: " + 'When `/crank` is invoked without an epic-id, check the preceding conversation for context:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core-kit/skills/crank/SKILL.md')
    assert '2. **Recently discussed epic** - If an epic was mentioned in conversation, use it' in text, "expected to find: " + '2. **Recently discussed epic** - If an epic was mentioned in conversation, use it'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core-kit/skills/crank/SKILL.md')
    assert '"Which epic should I crank? Run `bd list --type=epic` to see available epics."' in text, "expected to find: " + '"Which epic should I crank? Run `bd list --type=epic` to see available epics."'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/general-kit/skills/validation-chain/SKILL.md')
    assert 'plugins/general-kit/skills/validation-chain/SKILL.md' in text, "expected to find: " + 'plugins/general-kit/skills/validation-chain/SKILL.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/general-kit/skills/vibe-docs/SKILL.md')
    assert 'plugins/general-kit/skills/vibe-docs/SKILL.md' in text, "expected to find: " + 'plugins/general-kit/skills/vibe-docs/SKILL.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/general-kit/skills/vibe/SKILL.md')
    assert '2. **Recent code changes in conversation** - If code was just written or edited, validate those files' in text, "expected to find: " + '2. **Recent code changes in conversation** - If code was just written or edited, validate those files'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/general-kit/skills/vibe/SKILL.md')
    assert 'When `/vibe` is invoked without a target, check the preceding conversation for context:' in text, "expected to find: " + 'When `/vibe` is invoked without a target, check the preceding conversation for context:'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/general-kit/skills/vibe/SKILL.md')
    assert '3. **Staged git changes** - If `git diff --cached` shows staged files, validate those' in text, "expected to find: " + '3. **Staged git changes** - If `git diff --cached` shows staged files, validate those'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/vibe-kit/skills/validation-chain/SKILL.md')
    assert 'plugins/vibe-kit/skills/validation-chain/SKILL.md' in text, "expected to find: " + 'plugins/vibe-kit/skills/validation-chain/SKILL.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/vibe-kit/skills/vibe-docs/SKILL.md')
    assert 'plugins/vibe-kit/skills/vibe-docs/SKILL.md' in text, "expected to find: " + 'plugins/vibe-kit/skills/vibe-docs/SKILL.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/vibe-kit/skills/vibe/SKILL.md')
    assert '2. **Recent code changes in conversation** - If code was just written or edited, validate those files' in text, "expected to find: " + '2. **Recent code changes in conversation** - If code was just written or edited, validate those files'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/vibe-kit/skills/vibe/SKILL.md')
    assert 'When `/vibe` is invoked without a target, check the preceding conversation for context:' in text, "expected to find: " + 'When `/vibe` is invoked without a target, check the preceding conversation for context:'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/vibe-kit/skills/vibe/SKILL.md')
    assert '3. **Staged git changes** - If `git diff --cached` shows staged files, validate those' in text, "expected to find: " + '3. **Staged git changes** - If `git diff --cached` shows staged files, validate those'[:80]

