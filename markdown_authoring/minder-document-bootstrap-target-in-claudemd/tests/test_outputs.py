"""Behavioral checks for minder-document-bootstrap-target-in-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/minder")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Note**: Run `make bootstrap` once after cloning the repository. You may need to run it again if build tool versions change.' in text, "expected to find: " + '**Note**: Run `make bootstrap` once after cloning the repository. You may need to run it again if build tool versions change.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Before building or running Minder, install all build dependencies and initialize configuration:' in text, "expected to find: " + 'Before building or running Minder, install all build dependencies and initialize configuration:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Create `config.yaml` and `server-config.yaml` from example templates (if they don't exist)" in text, "expected to find: " + "- Create `config.yaml` and `server-config.yaml` from example templates (if they don't exist)"[:80]

