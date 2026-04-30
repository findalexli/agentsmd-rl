"""Behavioral checks for mega-add-copilotinstructionsmd-for-github-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mega")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Mega is an unofficial open-source implementation of Google Piper: a monorepo/monolithic codebase management system with Git compatibility, FUSE mounting, and Buck2 integration. When proposing designs ' in text, "expected to find: " + 'Mega is an unofficial open-source implementation of Google Piper: a monorepo/monolithic codebase management system with Git compatibility, FUSE mounting, and Buck2 integration. When proposing designs '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- When dealing with Git objects/packs, consider delta-chain depth, fanout tables, OID (SHA-1 vs SHA-256), and zstd/deflate trade-offs. Include micro-benchmarks for hot paths via criterion.' in text, "expected to find: " + '- When dealing with Git objects/packs, consider delta-chain depth, fanout tables, OID (SHA-1 vs SHA-256), and zstd/deflate trade-offs. Include micro-benchmarks for hot paths via criterion.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '* **DO:** When asked about building or testing, refer to the **Buck2** build system. Avoid suggesting root-level `cargo` or `npm` commands unless they are specific to a sub-package.' in text, "expected to find: " + '* **DO:** When asked about building or testing, refer to the **Buck2** build system. Avoid suggesting root-level `cargo` or `npm` commands unless they are specific to a sub-package.'[:80]

