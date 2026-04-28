"""Behavioral checks for images-add-instructions-for-copilot-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/images")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Example: PR #1548 switched `src/typescript-node/.devcontainer/Dockerfile` to the `4-*` JavaScript base, so `src/typescript-node/manifest.json` moved from 3.0.3 to 4.0.0, added the `*-trixie` variant' in text, "expected to find: " + '- Example: PR #1548 switched `src/typescript-node/.devcontainer/Dockerfile` to the `4-*` JavaScript base, so `src/typescript-node/manifest.json` moved from 3.0.3 to 4.0.0, added the `*-trixie` variant'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Breaking changes (for example, swapping the base OS) require a major bump; new non-breaking features require a minor bump; security or bug fixes require a patch bump.' in text, "expected to find: " + '- Breaking changes (for example, swapping the base OS) require a major bump; new non-breaking features require a minor bump; security or bug fixes require a patch bump.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Adding a variant means updating the architecture entry in `manifest.json`, listing the variant in `variantTags`, and setting it as `latest` unless it is a preview.' in text, "expected to find: " + '- Adding a variant means updating the architecture entry in `manifest.json`, listing the variant in `variantTags`, and setting it as `latest` unless it is a preview.'[:80]

