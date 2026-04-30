"""Behavioral checks for aidevops-t10814-update-agentsmd-document-daily (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aidevops")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert '**Daily skill refresh**: Each auto-update check also runs a 24h-gated skill freshness check. If >24h have passed since the last check, `skill-update-helper.sh --auto-update --quiet` pulls upstream cha' in text, "expected to find: " + '**Daily skill refresh**: Each auto-update check also runs a 24h-gated skill freshness check. If >24h have passed since the last check, `skill-update-helper.sh --auto-update --quiet` pulls upstream cha'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert '**Skill persistence**: Imported skills are stored in `~/.aidevops/agents/` and tracked in `configs/skill-sources.json`. The daily auto-update skill refresh (see Auto-Update above) keeps them current f' in text, "expected to find: " + '**Skill persistence**: Imported skills are stored in `~/.aidevops/agents/` and tracked in `configs/skill-sources.json`. The daily auto-update skill refresh (see Auto-Update above) keeps them current f'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert '**Repo version wins on update**: When `aidevops update` runs, shared agents in `~/.aidevops/agents/` are overwritten by the repo version. Only `custom/` and `draft/` directories are preserved. Importe' in text, "expected to find: " + '**Repo version wins on update**: When `aidevops update` runs, shared agents in `~/.aidevops/agents/` are overwritten by the repo version. Only `custom/` and `draft/` directories are preserved. Importe'[:80]

