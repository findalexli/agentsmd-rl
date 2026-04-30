"""Behavioral checks for jabref-restructure-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jabref")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Follow JabRef's code style rules as documented in [docs/getting-into-the-code/guidelines-for-setting-up-a-local-workspace/intellij-13-code-style.md](docs/getting-into-the-code/guidelines-for-setting" in text, "expected to find: " + "- Follow JabRef's code style rules as documented in [docs/getting-into-the-code/guidelines-for-setting-up-a-local-workspace/intellij-13-code-style.md](docs/getting-into-the-code/guidelines-for-setting"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> This project does not accept fully AI-generated pull requests. AI tools may be used assistively only. You must understand and take responsibility for every change you submit.' in text, "expected to find: " + '> This project does not accept fully AI-generated pull requests. AI tools may be used assistively only. You must understand and take responsibility for every change you submit.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document defines rules and expectations for **automated agents** (AI tools, bots, scripts) interacting with the JabRef repositories.' in text, "expected to find: " + 'This document defines rules and expectations for **automated agents** (AI tools, bots, scripts) interacting with the JabRef repositories.'[:80]

