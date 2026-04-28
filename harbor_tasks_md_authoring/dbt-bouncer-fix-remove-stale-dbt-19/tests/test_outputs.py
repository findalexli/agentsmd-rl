"""Behavioral checks for dbt-bouncer-fix-remove-stale-dbt-19 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dbt-bouncer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build-artifacts/SKILL.md')
    assert 'This generates fixtures for dbt 1.10 and 1.11 in `tests/fixtures/dbt_1X/target/` (manifest.json, catalog.json, run_results.json). Note: dbt 1.9 fixtures are frozen and not regenerated.' in text, "expected to find: " + 'This generates fixtures for dbt 1.10 and 1.11 in `tests/fixtures/dbt_1X/target/` (manifest.json, catalog.json, run_results.json). Note: dbt 1.9 fixtures are frozen and not regenerated.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `make build-artifacts` | Regenerate test fixtures (dbt 1.10, 1.11) |' in text, "expected to find: " + '| `make build-artifacts` | Regenerate test fixtures (dbt 1.10, 1.11) |'[:80]

