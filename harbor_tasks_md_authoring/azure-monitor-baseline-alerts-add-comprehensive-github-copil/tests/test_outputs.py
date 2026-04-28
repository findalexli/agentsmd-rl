"""Behavioral checks for azure-monitor-baseline-alerts-add-comprehensive-github-copil (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/azure-monitor-baseline-alerts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Azure Monitor Baseline Alerts (AMBA) is a comprehensive repository providing baseline alerting guidance and Infrastructure as Code (IaC) templates for Azure resources. The project includes a Hugo-base' in text, "expected to find: " + 'Azure Monitor Baseline Alerts (AMBA) is a comprehensive repository providing baseline alerting guidance and Infrastructure as Code (IaC) templates for Azure resources. The project includes a Hugo-base'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '4. Regenerate outputs: `cd tooling/export-alerts && python export-alerts.py --path ../../services --template ./alerts-template.xlsx --output-xls ../../services/amba-alerts.xlsx --output-json ../../ser' in text, "expected to find: " + '4. Regenerate outputs: `cd tooling/export-alerts && python export-alerts.py --path ../../services --template ./alerts-template.xlsx --output-xls ../../services/amba-alerts.xlsx --output-json ../../ser'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'python export-alerts.py --path ../../services --template ./alerts-template.xlsx --output-xls ../../services/amba-alerts.xlsx --output-json ../../services/amba-alerts.json --output-yaml ../../services/' in text, "expected to find: " + 'python export-alerts.py --path ../../services --template ./alerts-template.xlsx --output-xls ../../services/amba-alerts.xlsx --output-json ../../services/amba-alerts.json --output-yaml ../../services/'[:80]

