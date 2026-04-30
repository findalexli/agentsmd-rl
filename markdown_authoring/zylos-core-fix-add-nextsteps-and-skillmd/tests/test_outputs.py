"""Behavioral checks for zylos-core-fix-add-nextsteps-and-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/zylos-core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/component-management/references/install.md')
    assert '5. **Next Steps**: If `skill.nextSteps` exists, follow the instructions — this typically includes post-service-start guidance (e.g., configuring webhook URLs, optional security settings). Always show ' in text, "expected to find: " + '5. **Next Steps**: If `skill.nextSteps` exists, follow the instructions — this typically includes post-service-start guidance (e.g., configuring webhook URLs, optional security settings). Always show '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/component-management/references/install.md')
    assert "6. **SKILL.md**: If the component's SKILL.md has additional setup documentation beyond the frontmatter, read and follow it for any remaining configuration steps." in text, "expected to find: " + "6. **SKILL.md**: If the component's SKILL.md has additional setup documentation beyond the frontmatter, read and follow it for any remaining configuration steps."[:80]

