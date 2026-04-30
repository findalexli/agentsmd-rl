"""Behavioral checks for nanoclaw-feat-add-optin-diagnostics-via (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert 'Read and follow [diagnostics.md](diagnostics.md).' in text, "expected to find: " + 'Read and follow [diagnostics.md](diagnostics.md).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert '## Diagnostics' in text, "expected to find: " + '## Diagnostics'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/diagnostics.md')
    assert '3. Remove the "Diagnostics" section from both `.claude/skills/setup/SKILL.md` and `.claude/skills/update-nanoclaw/SKILL.md`' in text, "expected to find: " + '3. Remove the "Diagnostics" section from both `.claude/skills/setup/SKILL.md` and `.claude/skills/update-nanoclaw/SKILL.md`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/diagnostics.md')
    assert "curl -s -X POST https://us.i.posthog.com/capture/ -H 'Content-Type: application/json' -d @/tmp/nanoclaw-diagnostics.json" in text, "expected to find: " + "curl -s -X POST https://us.i.posthog.com/capture/ -H 'Content-Type: application/json' -d @/tmp/nanoclaw-diagnostics.json"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/diagnostics.md')
    assert '2. Replace contents of `.claude/skills/update-nanoclaw/diagnostics.md` with `# Diagnostics — opted out`' in text, "expected to find: " + '2. Replace contents of `.claude/skills/update-nanoclaw/diagnostics.md` with `# Diagnostics — opted out`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/SKILL.md')
    assert 'Read and follow [diagnostics.md](diagnostics.md).' in text, "expected to find: " + 'Read and follow [diagnostics.md](diagnostics.md).'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/SKILL.md')
    assert '## Diagnostics' in text, "expected to find: " + '## Diagnostics'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/diagnostics.md')
    assert '3. Remove the "Diagnostics" section from both `.claude/skills/setup/SKILL.md` and `.claude/skills/update-nanoclaw/SKILL.md`' in text, "expected to find: " + '3. Remove the "Diagnostics" section from both `.claude/skills/setup/SKILL.md` and `.claude/skills/update-nanoclaw/SKILL.md`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/diagnostics.md')
    assert "curl -s -X POST https://us.i.posthog.com/capture/ -H 'Content-Type: application/json' -d @/tmp/nanoclaw-diagnostics.json" in text, "expected to find: " + "curl -s -X POST https://us.i.posthog.com/capture/ -H 'Content-Type: application/json' -d @/tmp/nanoclaw-diagnostics.json"[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/diagnostics.md')
    assert '2. Replace contents of `.claude/skills/update-nanoclaw/diagnostics.md` with `# Diagnostics — opted out`' in text, "expected to find: " + '2. Replace contents of `.claude/skills/update-nanoclaw/diagnostics.md` with `# Diagnostics — opted out`'[:80]

