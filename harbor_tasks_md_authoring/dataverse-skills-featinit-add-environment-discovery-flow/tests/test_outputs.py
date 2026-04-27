"""Behavioral checks for dataverse-skills-featinit-add-environment-discovery-flow (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dataverse-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert '> **Note:** `pac admin create` requires tenant admin or Power Platform admin permissions. If it fails with a permissions error, guide the user to create the environment in the [Power Platform Admin Ce' in text, "expected to find: " + '> **Note:** `pac admin create` requires tenant admin or Power Platform admin permissions. If it fails with a permissions error, guide the user to create the environment in the [Power Platform Admin Ce'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert 'Before asking the user for a Dataverse environment URL, **check what is already available**. This avoids unnecessary questions and handles the common cases: the user is already connected, wants to pic' in text, "expected to find: " + 'Before asking the user for a Dataverse environment URL, **check what is already available**. This avoids unnecessary questions and handles the common cases: the user is already connected, wants to pic'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert 'Run the **Environment Discovery** flow (see section above) to determine the target environment. The user may want to use the currently active environment, pick a different one, or create a new one — t' in text, "expected to find: " + 'Run the **Environment Discovery** flow (see section above) to determine the target environment. The user may want to use the currently active environment, pick a different one, or create a new one — t'[:80]

