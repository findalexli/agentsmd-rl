"""Behavioral checks for vm0-docs-add-development-environment-section (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vm0")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **main branch is always stable** - All code merged to main has passed CI (build + tests). If your branch fails to build or pass tests, the issue is in your branch code, not main.' in text, "expected to find: " + '- **main branch is always stable** - All code merged to main has passed CI (build + tests). If your branch fails to build or pass tests, the issue is in your branch code, not main.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Use dev-tunnel for local development** - Run `/dev-tunnel` to start a local server accessible by sandbox webhooks. Without this, webhooks cannot reach your local server.' in text, "expected to find: " + '- **Use dev-tunnel for local development** - Run `/dev-tunnel` to start a local server accessible by sandbox webhooks. Without this, webhooks cannot reach your local server.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Run `script/sync-env.sh` to sync environment variables** - If missing required environment variables, ask the user to run this script to sync `.env.local`.' in text, "expected to find: " + '- **Run `script/sync-env.sh` to sync environment variables** - If missing required environment variables, ask the user to run this script to sync `.env.local`.'[:80]

