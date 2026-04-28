"""Behavioral checks for llamafactory-add-github-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/llamafactory")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Note**: Training configurations require GPU machines, so training is typically not tested end-to-end. Use `make test` to validate file-level functionality.' in text, "expected to find: " + '- **Note**: Training configurations require GPU machines, so training is typically not tested end-to-end. Use `make test` to validate file-level functionality.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Run tests with: `make test` (which runs `WANDB_DISABLED=true pytest -vv --import-mode=importlib tests/ tests_v1/`)' in text, "expected to find: " + '- Run tests with: `make test` (which runs `WANDB_DISABLED=true pytest -vv --import-mode=importlib tests/ tests_v1/`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'LLaMA Factory has two parallel architectures that can be switched via the `USE_V1` environment variable:' in text, "expected to find: " + 'LLaMA Factory has two parallel architectures that can be switched via the `USE_V1` environment variable:'[:80]

