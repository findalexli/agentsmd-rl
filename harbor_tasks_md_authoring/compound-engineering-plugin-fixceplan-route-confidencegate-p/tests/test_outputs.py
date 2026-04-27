"""Behavioral checks for compound-engineering-plugin-fixceplan-route-confidencegate-p (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/AGENTS.md')
    assert 'Developers of this plugin also use it via their marketplace install (`~/.claude/plugins/`). When a developer reports a bug they experienced while using a skill or agent, the installed version may be o' in text, "expected to find: " + 'Developers of this plugin also use it via their marketplace install (`~/.claude/plugins/`). When a developer reports a bug they experienced while using a skill or agent, the installed version may be o'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/AGENTS.md')
    assert "Important: Just because the developer's installed plugin may be out of date, it's possible both old and current repo versions have the bug. The proper fix is to still fix the repo version." in text, "expected to find: " + "Important: Just because the developer's installed plugin may be out of date, it's possible both old and current repo versions have the bug. The proper fix is to still fix the repo version."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/AGENTS.md')
    assert "- **Repo already has the fix**: The developer's install is stale. Tell them to reinstall the plugin or use `--plugin-dir` to load skills from the repo checkout. No code change needed." in text, "expected to find: " + "- **Repo already has the fix**: The developer's install is stale. Tell them to reinstall the plugin or use `--plugin-dir` to load skills from the repo checkout. No code change needed."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert 'If the plan already appears sufficiently grounded and the thin-grounding override does not apply, report "Confidence check passed — no sections need strengthening" and skip to Phase 5.3.8 (Document Re' in text, "expected to find: " + 'If the plan already appears sufficiently grounded and the thin-grounding override does not apply, report "Confidence check passed — no sections need strengthening" and skip to Phase 5.3.8 (Document Re'[:80]

