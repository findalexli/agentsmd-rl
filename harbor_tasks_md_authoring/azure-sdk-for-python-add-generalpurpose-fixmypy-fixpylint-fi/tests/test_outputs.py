"""Behavioral checks for azure-sdk-for-python-add-generalpurpose-fixmypy-fixpylint-fi (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/azure-sdk-for-python")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-black/SKILL.md')
    assert 'This skill automatically fixes black code formatting issues in any Azure SDK for Python package.' in text, "expected to find: " + 'This skill automatically fixes black code formatting issues in any Azure SDK for Python package.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-black/SKILL.md')
    assert 'description: Automatically fix black code formatting issues in any Azure SDK for Python package' in text, "expected to find: " + 'description: Automatically fix black code formatting issues in any Azure SDK for Python package'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-black/SKILL.md')
    assert '- The Azure SDK uses `eng/black-pyproject.toml` for repo-wide configuration' in text, "expected to find: " + '- The Azure SDK uses `eng/black-pyproject.toml` for repo-wide configuration'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-mypy/SKILL.md')
    assert 'Create a pull request with a descriptive title and body referencing the issue. Include what was fixed and confirm all mypy checks pass. The PR title should follow the format: "fix(<package-name>): Res' in text, "expected to find: " + 'Create a pull request with a descriptive title and body referencing the issue. Include what was fixed and confirm all mypy checks pass. The PR title should follow the format: "fix(<package-name>): Res'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-mypy/SKILL.md')
    assert '> **Note:** `azpysdk mypy` runs with a pinned version of mypy at the package level only. To focus on specific files, run the full check and filter the output by file path.' in text, "expected to find: " + '> **Note:** `azpysdk mypy` runs with a pinned version of mypy at the package level only. To focus on specific files, run the full check and filter the output by file path.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-mypy/SKILL.md')
    assert 'This skill automatically fixes mypy type checking errors in any Azure SDK for Python package by analyzing existing code patterns and applying fixes with 100% confidence.' in text, "expected to find: " + 'This skill automatically fixes mypy type checking errors in any Azure SDK for Python package by analyzing existing code patterns and applying fixes with 100% confidence.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-pylint/SKILL.md')
    assert 'Create a pull request with a descriptive title and body referencing the issue. Include what was fixed and confirm all pylint checks pass. The PR title should follow the format: "fix(<package-name>): R' in text, "expected to find: " + 'Create a pull request with a descriptive title and body referencing the issue. Include what was fixed and confirm all pylint checks pass. The PR title should follow the format: "fix(<package-name>): R'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-pylint/SKILL.md')
    assert '**Important: Do not run black as part of the pylint fix workflow.** Running black will reformat the code and may mask or change the pylint warnings you are trying to fix. Only run pylint to identify a' in text, "expected to find: " + '**Important: Do not run black as part of the pylint fix workflow.** Running black will reformat the code and may mask or change the pylint warnings you are trying to fix. Only run pylint to identify a'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-pylint/SKILL.md')
    assert '> **Note:** `azpysdk pylint` runs with a pinned version of pylint at the package level only. To focus on specific files, run the full check and filter the output by file path.' in text, "expected to find: " + '> **Note:** `azpysdk pylint` runs with a pinned version of pylint at the package level only. To focus on specific files, run the full check and filter the output by file path.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-sphinx/SKILL.md')
    assert 'Create a pull request with a descriptive title and body referencing the issue. Include what was fixed and confirm all Sphinx documentation checks pass. The PR title should follow the format: "fix(<pac' in text, "expected to find: " + 'Create a pull request with a descriptive title and body referencing the issue. Include what was fixed and confirm all Sphinx documentation checks pass. The PR title should follow the format: "fix(<pac'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-sphinx/SKILL.md')
    assert 'This skill automatically fixes Sphinx documentation warnings and errors in any Azure SDK for Python package by analyzing existing documentation patterns and applying fixes with 100% confidence.' in text, "expected to find: " + 'This skill automatically fixes Sphinx documentation warnings and errors in any Azure SDK for Python package by analyzing existing documentation patterns and applying fixes with 100% confidence.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/fix-sphinx/SKILL.md')
    assert 'Ask: "Please provide either the GitHub issue URL or the package path (e.g. sdk/storage/azure-storage-blob) for the Sphinx documentation problems you want to fix."' in text, "expected to find: " + 'Ask: "Please provide either the GitHub issue URL or the package path (e.g. sdk/storage/azure-storage-blob) for the Sphinx documentation problems you want to fix."'[:80]

