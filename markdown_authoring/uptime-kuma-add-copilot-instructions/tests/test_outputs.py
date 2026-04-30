"""Behavioral checks for uptime-kuma-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/uptime-kuma")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Uptime Kuma** is a self-hosted monitoring tool for HTTP(s), TCP, DNS, Docker, etc. Built with Vue 3 (frontend) and Node.js/Express (backend), using Socket.IO for real-time communication.' in text, "expected to find: " + '**Uptime Kuma** is a self-hosted monitoring tool for HTTP(s), TCP, DNS, Docker, etc. Built with Vue 3 (frontend) and Node.js/Express (backend), using Socket.IO for real-time communication.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "2. **Dependencies**: 5 known vulnerabilities (3 moderate, 2 high) - acknowledged, don't fix without discussion" in text, "expected to find: " + "2. **Dependencies**: 5 known vulnerabilities (3 moderate, 2 high) - acknowledged, don't fix without discussion"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "2. **TypeScript errors**: `npm run tsc` shows 1400+ errors - ignore them, they don't affect builds" in text, "expected to find: " + "2. **TypeScript errors**: `npm run tsc` shows 1400+ errors - ignore them, they don't affect builds"[:80]

