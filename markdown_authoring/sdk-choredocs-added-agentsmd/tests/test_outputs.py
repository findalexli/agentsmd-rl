"""Behavioral checks for sdk-choredocs-added-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Key attributes**: `func` (your training function), `func_args`, `packages_to_install`, `pip_index_urls`, `num_nodes`, `resources_per_node`, `env`' in text, "expected to find: " + '- **Key attributes**: `func` (your training function), `func_args`, `packages_to_install`, `pip_index_urls`, `num_nodes`, `resources_per_node`, `env`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Unit test structure must be consistent between each other (see `kubeflow/trainer/backends/kubernetes/backend_test.py` for reference)' in text, "expected to find: " + '- Unit test structure must be consistent between each other (see `kubeflow/trainer/backends/kubernetes/backend_test.py` for reference)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Naming: pep8-naming; functions/vars `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`; prefix private with `_`' in text, "expected to find: " + '- Naming: pep8-naming; functions/vars `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`; prefix private with `_`'[:80]

