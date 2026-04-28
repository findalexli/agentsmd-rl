"""Behavioral checks for shovel-heroes-doc-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shovel-heroes")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";' in text, "expected to find: " + 'import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "type VolunteerRegistration = components['schemas']['VolunteerRegistration'];" in text, "expected to find: " + "type VolunteerRegistration = components['schemas']['VolunteerRegistration'];"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- `react/no-unknown-property`: 'off' - 允許自訂 JSX 屬性（如 cmdk-*, toast-*）" in text, "expected to find: " + "- `react/no-unknown-property`: 'off' - 允許自訂 JSX 屬性（如 cmdk-*, toast-*）"[:80]

