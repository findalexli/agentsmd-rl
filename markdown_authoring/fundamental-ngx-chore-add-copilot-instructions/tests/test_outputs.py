"""Behavioral checks for fundamental-ngx-chore-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fundamental-ngx")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'You are a dedicated Angular developer who thrives on leveraging the absolute latest features of the framework to build cutting-edge components. You are currently immersed in Angular v20+, passionately' in text, "expected to find: " + 'You are a dedicated Angular developer who thrives on leveraging the absolute latest features of the framework to build cutting-edge components. You are currently immersed in Angular v20+, passionately'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**When implementing changes, you always explain and reason about your decisions.** You provide clear context for why specific approaches are chosen, how they align with Angular and NX best practices, ' in text, "expected to find: " + '**When implementing changes, you always explain and reason about your decisions.** You provide clear context for why specific approaches are chosen, how they align with Angular and NX best practices, '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'You are working in an **NX monorepo** structure with multiple libraries including core, platform, cdk, btp, cx, i18n, datetime-adapter, and ui5-webcomponents. You understand the NX workspace architect' in text, "expected to find: " + 'You are working in an **NX monorepo** structure with multiple libraries including core, platform, cdk, btp, cx, i18n, datetime-adapter, and ui5-webcomponents. You understand the NX workspace architect'[:80]

