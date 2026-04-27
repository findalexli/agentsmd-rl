"""Behavioral checks for webhook-skills-docs-update-agentsmd-with-detailed (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/webhook-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This runs all example tests and uses Claude to review the skill against provider documentation for accuracy. See [CONTRIBUTING.md](CONTRIBUTING.md) for acceptance thresholds (0 critical, ≤1 major, ≤2 ' in text, "expected to find: " + 'This runs all example tests and uses Claude to review the skill against provider documentation for accuracy. See [CONTRIBUTING.md](CONTRIBUTING.md) for acceptance thresholds (0 critical, ≤1 major, ≤2 '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **scripts/test-agent-scenario.sh** — At least one scenario added (e.g. `{provider}-express`) in both `usage()` and `get_scenario_config()`' in text, "expected to find: " + '2. **scripts/test-agent-scenario.sh** — At least one scenario added (e.g. `{provider}-express`) in both `usage()` and `get_scenario_config()`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The automated review checks skill content and tests, but does **not** verify integration with repository infrastructure. Manually confirm:' in text, "expected to find: " + 'The automated review checks skill content and tests, but does **not** verify integration with repository infrastructure. Manually confirm:'[:80]

