"""Behavioral checks for mzmine-add-codex-skills-for-mvci (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mzmine")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mvci-gui/SKILL.md')
    assert 'description: Use a MVC or MVCI architecture when building complex user interface components with multiple controls or panes and if the user requests the MVC/MVCI architecture. For simpler interfaces, ' in text, "expected to find: " + 'description: Use a MVC or MVCI architecture when building complex user interface components with multiple controls or panes and if the user requests the MVC/MVCI architecture. For simpler interfaces, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mvci-gui/SKILL.md')
    assert '- Prefer bindings from the View to the Model over listeners. Use bidirectional bindings if possible.' in text, "expected to find: " + '- Prefer bindings from the View to the Model over listeners. Use bidirectional bindings if possible.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mvci-gui/SKILL.md')
    assert "- The ViewBuilder is responsible for logic that reflects the Controller's or Interactor's changes to" in text, "expected to find: " + "- The ViewBuilder is responsible for logic that reflects the Controller's or Interactor's changes to"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/new-chart/SKILL.md')
    assert '- When creating new charts, check if we have an appropriate chart, dataset and/or renderer in' in text, "expected to find: " + '- When creating new charts, check if we have an appropriate chart, dataset and/or renderer in'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/new-chart/SKILL.md')
    assert 'description: How to create a new chart, renderer, label generator in the mzmine framework.' in text, "expected to find: " + 'description: How to create a new chart, renderer, label generator in the mzmine framework.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/new-chart/SKILL.md')
    assert '- When reacting to Chart items, check if we have the property exposed in FxBaseChartModel,' in text, "expected to find: " + '- When reacting to Chart items, check if we have the property exposed in FxBaseChartModel,'[:80]

