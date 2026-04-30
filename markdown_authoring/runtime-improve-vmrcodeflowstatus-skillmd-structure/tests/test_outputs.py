"""Behavioral checks for runtime-improve-vmrcodeflowstatus-skillmd-structure (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/runtime")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/vmr-codeflow-status/SKILL.md')
    assert 'description: Analyze VMR codeflow PR status for dotnet repositories. Use when investigating stale codeflow PRs, checking if fixes have flowed through the VMR pipeline, debugging dependency update issu' in text, "expected to find: " + 'description: Analyze VMR codeflow PR status for dotnet repositories. Use when investigating stale codeflow PRs, checking if fixes have flowed through the VMR pipeline, debugging dependency update issu'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/vmr-codeflow-status/SKILL.md')
    assert "> ⚠️ **Common mistake**: Don't use `-PRNumber` and `-CheckMissing` together — they are separate modes. `-CheckMissing` scans branches discovered from open and recent backflow PRs (unless `-Branch` is " in text, "expected to find: " + "> ⚠️ **Common mistake**: Don't use `-PRNumber` and `-CheckMissing` together — they are separate modes. `-CheckMissing` scans branches discovered from open and recent backflow PRs (unless `-Branch` is "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/vmr-codeflow-status/SKILL.md')
    assert '- You\'re asked questions like "is this codeflow PR up to date", "has the runtime revert reached this PR", "why is the codeflow blocked", "what is the state of flow for the sdk", "what\'s the flow statu' in text, "expected to find: " + '- You\'re asked questions like "is this codeflow PR up to date", "has the runtime revert reached this PR", "why is the codeflow blocked", "what is the state of flow for the sdk", "what\'s the flow statu'[:80]

