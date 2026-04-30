"""Behavioral checks for farmer-add-github-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/farmer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'You can generally assume it will be in the next release based off the GitHub releases. Once the PR milestone is set, it will confirm what release the PR should be under in the release notes.' in text, "expected to find: " + 'You can generally assume it will be in the next release based off the GitHub releases. Once the PR milestone is set, it will confirm what release the PR should be under in the release notes.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Include this section: "Below is a minimal example configuration that includes the new features, which can be used to deploy to Azure:" followed by an F# code block with the example' in text, "expected to find: " + '- Include this section: "Below is a minimal example configuration that includes the new features, which can be used to deploy to Azure:" followed by an F# code block with the example'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**CRITICAL**: All F# code MUST be formatted with Fantomas before committing. This is automatically checked by CI and PRs will be rejected if formatting is not applied.' in text, "expected to find: " + '**CRITICAL**: All F# code MUST be formatted with Fantomas before committing. This is automatically checked by CI and PRs will be rejected if formatting is not applied.'[:80]

