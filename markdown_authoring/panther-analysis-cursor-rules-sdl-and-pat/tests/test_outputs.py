"""Behavioral checks for panther-analysis-cursor-rules-sdl-and-pat (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/panther-analysis")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/simple-detections.mdc')
    assert "You are an expert cybersecurity detection engineer specializing in Panther SIEM Simple Detection rules. Help users write effective detection rules using Panther's YAML-based Simple Detection format. W" in text, "expected to find: " + "You are an expert cybersecurity detection engineer specializing in Panther SIEM Simple Detection rules. Help users write effective detection rules using Panther's YAML-based Simple Detection format. W"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/simple-detections.mdc')
    assert '| `DynamicSeverities` | Alternate severities based on custom sets of conditions | List of dynamic severity configurations, consisting of `ChangeTo` and `Conditions` fields. `ChangeTo` is a Severity va' in text, "expected to find: " + '| `DynamicSeverities` | Alternate severities based on custom sets of conditions | List of dynamic severity configurations, consisting of `ChangeTo` and `Conditions` fields. `ChangeTo` is a Severity va'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/simple-detections.mdc')
    assert '| `Severity` | Which severity an associated alert should have | One of: `Info`, `Low`, `Medium`, `High`, or `Critical`. This field is overwritten by DynamicSeverities, but is required even if DynamicS' in text, "expected to find: " + '| `Severity` | Which severity an associated alert should have | One of: `Info`, `Low`, `Medium`, `High`, or `Critical`. This field is overwritten by DynamicSeverities, but is required even if DynamicS'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'pipenv run pat test --filter RuleID=AWS.IAM.AccessKeyCompromised --test-names "An AWS Access Key was Uploaded to Github"' in text, "expected to find: " + 'pipenv run pat test --filter RuleID=AWS.IAM.AccessKeyCompromised --test-names "An AWS Access Key was Uploaded to Github"'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'Files cannot be specifically passed as arguments, only the attributes in their metadata YML file, like RuleID.' in text, "expected to find: " + 'Files cannot be specifically passed as arguments, only the attributes in their metadata YML file, like RuleID.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'Use the `panther_analysis_tool` aka `pat` to run tests for detections:' in text, "expected to find: " + 'Use the `panther_analysis_tool` aka `pat` to run tests for detections:'[:80]

