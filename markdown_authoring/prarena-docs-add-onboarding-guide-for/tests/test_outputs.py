"""Behavioral checks for prarena-docs-add-onboarding-guide-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prarena")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Update the first row in both `data.csv` and `data_backup.csv` so the header now contains the three new `<key>_*` columns. If a migration is needed, either backfill realistic values by querying the A' in text, "expected to find: " + '- Update the first row in both `data.csv` and `data_backup.csv` so the header now contains the three new `<key>_*` columns. If a migration is needed, either backfill realistic values by querying the A'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- JSON export: add the color triple to the `colors` dictionary and include the new key in every `for agent in [...]` list. (Search for `for agent in ["copilot", "codex", "cursor", "devin", "codegen", ' in text, "expected to find: " + '- JSON export: add the color triple to the `colors` dictionary and include the new key in every `for agent in [...]` list. (Search for `for agent in ["copilot", "codex", "cursor", "devin", "codegen", '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Update the `row` list and the CSV header block right below it to append the new metrics. Order matters – keep all metrics grouped by agent, and ensure the header labels exactly match the keys from `' in text, "expected to find: " + '- Update the `row` list and the CSV header block right below it to append the new metrics. Order matters – keep all metrics grouped by agent, and ensure the header labels exactly match the keys from `'[:80]

