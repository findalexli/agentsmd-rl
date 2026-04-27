"""Behavioral checks for mlflow-speed-up-skills-cli-by (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mlflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/README.md')
    assert 'Run `uv run --package skills skills --help` to see available commands.' in text, "expected to find: " + 'Run `uv run --package skills skills --help` to see available commands.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/README.md')
    assert 'uv run --package skills skills <command> [args]' in text, "expected to find: " + 'uv run --package skills skills <command> [args]'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-review-comment/SKILL.md')
    assert '- Bash(uv run --package skills skills fetch-diff:*)' in text, "expected to find: " + '- Bash(uv run --package skills skills fetch-diff:*)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/analyze-ci/SKILL.md')
    assert "uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/actions/runs/12345/job/67890'" in text, "expected to find: " + "uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/actions/runs/12345/job/67890'"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/analyze-ci/SKILL.md')
    assert "uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/actions/runs/22626454465'" in text, "expected to find: " + "uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/actions/runs/22626454465'"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/analyze-ci/SKILL.md')
    assert "uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/pull/19601'" in text, "expected to find: " + "uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/pull/19601'"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fetch-diff/SKILL.md')
    assert "uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files 'mlflow/server/js/*'" in text, "expected to find: " + "uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files 'mlflow/server/js/*'"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fetch-diff/SKILL.md')
    assert "uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py' '*.ts'" in text, "expected to find: " + "uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py' '*.ts'"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fetch-diff/SKILL.md')
    assert "uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py'" in text, "expected to find: " + "uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py'"[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fetch-unresolved-comments/SKILL.md')
    assert 'uv run --package skills skills fetch-unresolved-comments https://github.com/mlflow/mlflow/pull/18327' in text, "expected to find: " + 'uv run --package skills skills fetch-unresolved-comments https://github.com/mlflow/mlflow/pull/18327'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fetch-unresolved-comments/SKILL.md')
    assert '- Bash(uv run --package skills skills fetch-unresolved-comments:*)' in text, "expected to find: " + '- Bash(uv run --package skills skills fetch-unresolved-comments:*)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fetch-unresolved-comments/SKILL.md')
    assert 'uv run --package skills skills fetch-unresolved-comments <pr_url>' in text, "expected to find: " + 'uv run --package skills skills fetch-unresolved-comments <pr_url>'[:80]

