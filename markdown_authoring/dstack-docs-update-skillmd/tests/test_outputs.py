"""Behavioral checks for dstack-docs-update-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dstack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '**Grouping:** Prefer `--group-by gpu` (other supported values: `gpu,backend`, `gpu,backend,region`) for aggregated output across all offers, not `--max-offers`.' in text, "expected to find: " + '**Grouping:** Prefer `--group-by gpu` (other supported values: `gpu,backend`, `gpu,backend,region`) for aggregated output across all offers, not `--max-offers`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert 'Offers represent available instance configurations available for provisioning across backends. `dstack offer` lists offers regardless of configured fleets.' in text, "expected to find: " + 'Offers represent available instance configurations available for provisioning across backends. `dstack offer` lists offers regardless of configured fleets.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '**Max offers:** By default, `dstack offer` returns first N offers (output also includes the total number). Use `--max-offers N` to increase the limit.' in text, "expected to find: " + '**Max offers:** By default, `dstack offer` returns first N offers (output also includes the total number). Use `--max-offers N` to increase the limit.'[:80]

