"""Behavioral checks for ng-select-feat-add-angular-project-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ng-select")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rules.mdc')
    assert '- Prefer Angular control flow syntax (`@for`, `@if`, `@switch`) over legacy structural directives (`*ngFor`, `*ngIf`, `*ngSwitch`)' in text, "expected to find: " + '- Prefer Angular control flow syntax (`@for`, `@if`, `@switch`) over legacy structural directives (`*ngFor`, `*ngIf`, `*ngSwitch`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rules.mdc')
    assert "- Use `@Injectable({providedIn: 'root'})` for services unless a different scope is required" in text, "expected to find: " + "- Use `@Injectable({providedIn: 'root'})` for services unless a different scope is required"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rules.mdc')
    assert '- Ensure all code follows WCAG guidelines and Angular accessibility best practices' in text, "expected to find: " + '- Ensure all code follows WCAG guidelines and Angular accessibility best practices'[:80]

