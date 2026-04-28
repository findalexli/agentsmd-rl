"""Behavioral checks for bluefin-chorecopilot-update-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bluefin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "**Bluefin** is a cloud-native desktop operating system that reimagines the Linux desktop experience. It's an OS built on Fedora Linux using container technologies with atomic updates." in text, "expected to find: " + "**Bluefin** is a cloud-native desktop operating system that reimagines the Linux desktop experience. It's an OS built on Fedora Linux using container technologies with atomic updates."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**CRITICAL**: Packages are split into separate arrays to prevent COPR repos from injecting malicious versions of Fedora packages:' in text, "expected to find: " + '**CRITICAL**: Packages are split into separate arrays to prevent COPR repos from injecting malicious versions of Fedora packages:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `just fedora_version <image> <tag> <flavor>` - Dynamically detects Fedora version from upstream base images' in text, "expected to find: " + '- `just fedora_version <image> <tag> <flavor>` - Dynamically detects Fedora version from upstream base images'[:80]

