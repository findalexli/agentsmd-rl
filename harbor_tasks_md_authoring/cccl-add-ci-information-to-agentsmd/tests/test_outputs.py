"""Behavioral checks for cccl-add-ci-information-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cccl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* To reduce overhead, you can add an override matrix in `workflows.override`. This limits the PR CI run to a targeted subset of jobs. Overrides are recommended when:' in text, "expected to find: " + '* To reduce overhead, you can add an override matrix in `workflows.override`. This limits the PR CI run to a targeted subset of jobs. Overrides are recommended when:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* Changes touch high-dependency areas (e.g. top-level CI/devcontainers, libcudacxx, thrust, CUB). See `ci/inspect_changes.sh`\xa0for dependency information.' in text, "expected to find: " + '* Changes touch high-dependency areas (e.g. top-level CI/devcontainers, libcudacxx, thrust, CUB). See `ci/inspect_changes.sh`\xa0for dependency information.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* Defines internal dependencies between CCCL projects. If a project is marked dirty, all dependent projects are also marked dirty and tested.' in text, "expected to find: " + '* Defines internal dependencies between CCCL projects. If a project is marked dirty, all dependent projects are also marked dirty and tested.'[:80]

