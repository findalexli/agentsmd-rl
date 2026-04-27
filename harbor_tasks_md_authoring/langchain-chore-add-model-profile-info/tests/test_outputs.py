"""Behavioral checks for langchain-chore-add-model-profile-info (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/langchain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Model profiles are generated using the `langchain-profiles` CLI in `libs/model-profiles`. The `--data-dir` must point to the directory containing `profile_augmentations.toml`, not the top-level packag' in text, "expected to find: " + 'Model profiles are generated using the `langchain-profiles` CLI in `libs/model-profiles`. The `--data-dir` must point to the directory containing `profile_augmentations.toml`, not the top-level packag'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'echo y | uv run langchain-profiles refresh --provider google --data-dir /path/to/langchain-google/libs/genai/langchain_google_genai/data' in text, "expected to find: " + 'echo y | uv run langchain-profiles refresh --provider google --data-dir /path/to/langchain-google/libs/genai/langchain_google_genai/data'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The `echo y |` pipe is required when `--data-dir` is outside the `libs/model-profiles` working directory.' in text, "expected to find: " + 'The `echo y |` pipe is required when `--data-dir` is outside the `libs/model-profiles` working directory.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Model profiles are generated using the `langchain-profiles` CLI in `libs/model-profiles`. The `--data-dir` must point to the directory containing `profile_augmentations.toml`, not the top-level packag' in text, "expected to find: " + 'Model profiles are generated using the `langchain-profiles` CLI in `libs/model-profiles`. The `--data-dir` must point to the directory containing `profile_augmentations.toml`, not the top-level packag'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'echo y | uv run langchain-profiles refresh --provider google --data-dir /path/to/langchain-google/libs/genai/langchain_google_genai/data' in text, "expected to find: " + 'echo y | uv run langchain-profiles refresh --provider google --data-dir /path/to/langchain-google/libs/genai/langchain_google_genai/data'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The `echo y |` pipe is required when `--data-dir` is outside the `libs/model-profiles` working directory.' in text, "expected to find: " + 'The `echo y |` pipe is required when `--data-dir` is outside the `libs/model-profiles` working directory.'[:80]

