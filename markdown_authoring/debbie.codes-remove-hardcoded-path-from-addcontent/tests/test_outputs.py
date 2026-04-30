"""Behavioral checks for debbie.codes-remove-hardcoded-path-from-addcontent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/debbie.codes")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/environment.md')
    assert 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && npm run dev > /tmp/nuxt-dev.log 2>&1 &' in text, "expected to find: " + 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && npm run dev > /tmp/nuxt-dev.log 2>&1 &'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/environment.md')
    assert 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && npm install 2>&1 | tail -5' in text, "expected to find: " + 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && npm install 2>&1 | tail -5'[:80]

