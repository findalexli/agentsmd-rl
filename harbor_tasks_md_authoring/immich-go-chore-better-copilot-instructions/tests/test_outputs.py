"""Behavioral checks for immich-go-chore-better-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/immich-go")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'These instructions define how GitHub Copilot should assist with the maintenance and evolution of **immich-go**, a Go-based open-source CLI project, maintained by a single developer.' in text, "expected to find: " + 'These instructions define how GitHub Copilot should assist with the maintenance and evolution of **immich-go**, a Go-based open-source CLI project, maintained by a single developer.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Before merging any feature, refactor, or behavior change, Copilot must ensure that **project documentation remains accurate and consistent with the code**.' in text, "expected to find: " + 'Before merging any feature, refactor, or behavior change, Copilot must ensure that **project documentation remains accurate and consistent with the code**.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Large refactors must be broken down into **multiple small PRs** that can be merged independently to keep `main` / `develop` divergence minimal.' in text, "expected to find: " + 'Large refactors must be broken down into **multiple small PRs** that can be merged independently to keep `main` / `develop` divergence minimal.'[:80]

