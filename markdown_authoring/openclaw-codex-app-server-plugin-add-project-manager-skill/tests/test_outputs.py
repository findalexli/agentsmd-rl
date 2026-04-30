"""Behavioral checks for openclaw-codex-app-server-plugin-add-project-manager-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openclaw-codex-app-server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/project-manager/SKILL.md')
    assert '- GitHub Projects custom views are not well-supported by `gh` or GraphQL mutations. Reading views works, but creating/editing/copying views is still better done in the web UI or browser automation. `g' in text, "expected to find: " + '- GitHub Projects custom views are not well-supported by `gh` or GraphQL mutations. Reading views works, but creating/editing/copying views is still better done in the web UI or browser automation. `g'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/project-manager/SKILL.md')
    assert '- `gh project item-edit` needs opaque ids for the project, item, field, and single-select option. Always discover them with `gh project view ...` and `gh project field-list ...` instead of assuming ca' in text, "expected to find: " + '- `gh project item-edit` needs opaque ids for the project, item, field, and single-select option. Always discover them with `gh project view ...` and `gh project field-list ...` instead of assuming ca'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/project-manager/SKILL.md')
    assert '- `.local/issue-drafts/<nn>-<slug>.md` filenames are local scratch ids, not GitHub issue numbers. Keep them stable enough to reuse, but do not try to force them to match the eventual GitHub issue numb' in text, "expected to find: " + '- `.local/issue-drafts/<nn>-<slug>.md` filenames are local scratch ids, not GitHub issue numbers. Keep them stable enough to reuse, but do not try to force them to match the eventual GitHub issue numb'[:80]

