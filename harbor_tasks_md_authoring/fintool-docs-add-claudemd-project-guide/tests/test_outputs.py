"""Behavioral checks for fintool-docs-add-claudemd-project-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fintool")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Fintool is a suite of Rust CLI tools for agentic trading and market intelligence across multiple exchanges. Each exchange has its own dedicated binary. All CLIs support `--json` mode for scripting and' in text, "expected to find: " + 'Fintool is a suite of Rust CLI tools for agentic trading and market intelligence across multiple exchanges. Each exchange has its own dedicated binary. All CLIs support `--json` mode for scripting and'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "3. **Use CLI binaries, not raw APIs.** If an example needs to call a web API that isn't wrapped in a CLI binary, that's a sign the CLI is missing a feature. Add the feature to the CLI first, then call" in text, "expected to find: " + "3. **Use CLI binaries, not raw APIs.** If an example needs to call a web API that isn't wrapped in a CLI binary, that's a sign the CLI is missing a feature. Add the feature to the CLI first, then call"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. **Scripts must be in Python** (3.10+, stdlib only — no third-party packages). Use `subprocess` to call CLI binaries in `--json` mode. Do NOT call web APIs directly from Python.' in text, "expected to find: " + '2. **Scripts must be in Python** (3.10+, stdlib only — no third-party packages). Use `subprocess` to call CLI binaries in `--json` mode. Do NOT call web APIs directly from Python.'[:80]

