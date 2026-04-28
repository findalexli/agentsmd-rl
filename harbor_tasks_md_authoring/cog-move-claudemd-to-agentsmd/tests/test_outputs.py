"""Behavioral checks for cog-move-claudemd-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cog")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Python code is tested using `tox`, which allows testing across multiple Python versions and configurations. The `tox.ini` file defines different environments for testing, such as `py313-pydantic2-test' in text, "expected to find: " + 'Python code is tested using `tox`, which allows testing across multiple Python versions and configurations. The `tox.ini` file defines different environments for testing, such as `py313-pydantic2-test'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The integration tests require a built Cog binary, which defaults to the first `cog` in `PATH`. Run tests against a specific binary with the `COG_BINARY` environment variable. For example, to build cog' in text, "expected to find: " + 'The integration tests require a built Cog binary, which defaults to the first `cog` in `PATH`. Run tests against a specific binary with the `COG_BINARY` environment variable. For example, to build cog'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `uv run tox -e py312-pydantic2-tests -- python/tests/server/test_http.py::test_openapi_specification_with_yield` - Runs a specific Python test with a specific Pydantic version' in text, "expected to find: " + '- `uv run tox -e py312-pydantic2-tests -- python/tests/server/test_http.py::test_openapi_specification_with_yield` - Runs a specific Python test with a specific Pydantic version'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

