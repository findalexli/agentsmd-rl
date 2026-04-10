"""
Task: mlflow-fetchdiff-add-files-filter-option
Repo: mlflow @ 956ab37d911e777ce40740ab851d2d472cec2752
PR:   21451

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import argparse
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/mlflow"


# ---------------------------------------------------------------------------
# Import helper — mock the GitHub client dependency (not needed for tests)
# ---------------------------------------------------------------------------

def _import_fetch_diff():
    """Import fetch_diff module, mocking non-stdlib dependencies."""
    if "skills" not in sys.modules:
        skills_mod = types.ModuleType("skills")
        skills_mod.__path__ = [f"{REPO}/.claude/skills/src/skills"]
        sys.modules["skills"] = skills_mod
    if "skills.commands" not in sys.modules:
        commands_mod = types.ModuleType("skills.commands")
        commands_mod.__path__ = [f"{REPO}/.claude/skills/src/skills/commands"]
        sys.modules["skills.commands"] = commands_mod
    if "skills.github" not in sys.modules:
        github_mock = types.ModuleType("skills.github")
        github_mock.GitHubClient = MagicMock
        github_mock.parse_pr_url = MagicMock
        sys.modules["skills.github"] = github_mock

    src_path = f"{REPO}/.claude/skills/src"
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    from skills.commands.fetch_diff import filter_diff, register
    return filter_diff, register


# Sample diff with three file types for testing pattern filtering
SAMPLE_DIFF = (
    "diff --git a/src/main.py b/src/main.py\n"
    "index abc1234..def5678 100644\n"
    "--- a/src/main.py\n"
    "+++ b/src/main.py\n"
    "@@ -1,3 +1,3 @@\n"
    " import os\n"
    "-old_line = True\n"
    "+new_line = True\n"
    " end = False\n"
    "diff --git a/src/utils.ts b/src/utils.ts\n"
    "index abc1234..def5678 100644\n"
    "--- a/src/utils.ts\n"
    "+++ b/src/utils.ts\n"
    "@@ -1,3 +1,3 @@\n"
    " const x = 1;\n"
    "-const old_val = 2;\n"
    "+const updated = 2;\n"
    " const y = 3;\n"
    "diff --git a/docs/guide.md b/docs/guide.md\n"
    "index abc1234..def5678 100644\n"
    "--- a/docs/guide.md\n"
    "+++ b/docs/guide.md\n"
    "@@ -1,3 +1,3 @@\n"
    " # Guide\n"
    "-Old content\n"
    "+New content\n"
    " Footer"
)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    py_compile.compile(
        f"{REPO}/.claude/skills/src/skills/commands/fetch_diff.py",
        doraise=True,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filter_diff_single_pattern():
    """filter_diff with file_patterns=['*.py'] returns only Python file diffs."""
    filter_diff, _ = _import_fetch_diff()
    result = filter_diff(SAMPLE_DIFF, file_patterns=["*.py"])
    assert "src/main.py" in result
    assert "new_line = True" in result
    assert "src/utils.ts" not in result
    assert "docs/guide.md" not in result


# [pr_diff] fail_to_pass
def test_filter_diff_multiple_patterns():
    """filter_diff with multiple patterns returns files matching any pattern."""
    filter_diff, _ = _import_fetch_diff()
    result = filter_diff(SAMPLE_DIFF, file_patterns=["*.py", "*.ts"])
    assert "src/main.py" in result
    assert "src/utils.ts" in result
    assert "docs/guide.md" not in result


# [pr_diff] fail_to_pass
def test_filter_diff_path_glob():
    """filter_diff with path glob filters by directory prefix."""
    filter_diff, _ = _import_fetch_diff()
    result = filter_diff(SAMPLE_DIFF, file_patterns=["docs/*"])
    assert "docs/guide.md" in result
    assert "New content" in result
    assert "src/main.py" not in result
    assert "src/utils.ts" not in result


# [pr_diff] fail_to_pass
def test_register_adds_files_argument():
    """register() wires up --files nargs='+' CLI argument."""
    _, register = _import_fetch_diff()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register(subparsers)
    args = parser.parse_args(
        [
            "fetch-diff",
            "https://github.com/foo/bar/pull/1",
            "--files",
            "*.py",
            "*.ts",
        ]
    )
    assert args.files == ["*.py", "*.ts"]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/doc update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_documents_files_option():
    """SKILL.md must document the --files option."""
    skill_md = Path(REPO) / ".claude" / "skills" / "fetch-diff" / "SKILL.md"
    content = skill_md.read_text()
    assert "--files" in content


# [pr_diff] fail_to_pass
def test_skill_md_has_pattern_examples():
    """SKILL.md must include glob pattern usage examples."""
    skill_md = Path(REPO) / ".claude" / "skills" / "fetch-diff" / "SKILL.md"
    content = skill_md.read_text()
    assert "*.py" in content
    # Should show multi-pattern or path-based examples too
    assert "*.ts" in content or "*.js" in content or "server/" in content


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — backward compatibility
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_filter_diff_no_patterns_unchanged():
    """filter_diff without file_patterns returns all non-excluded files."""
    filter_diff, _ = _import_fetch_diff()
    result = filter_diff(SAMPLE_DIFF)
    assert "src/main.py" in result
    assert "src/utils.ts" in result
    assert "docs/guide.md" in result


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Ruff linter check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff==0.15.2"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    target = f"{REPO}/.claude/skills/src/skills/commands/fetch_diff.py"
    r = subprocess.run(
        ["python", "-m", "ruff", "check", target],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Ruff format check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff==0.15.2"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    target = f"{REPO}/.claude/skills/src/skills/commands/fetch_diff.py"
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", target],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_mypy():
    """Mypy type check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "mypy", "aiohttp", "pydantic", "claude-agent-sdk", "tiktoken", "typing_extensions"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"Failed to install mypy deps: {r.stderr}"

    target = f"{REPO}/.claude/skills/src/skills/commands/fetch_diff.py"
    r = subprocess.run(
        ["python", "-m", "mypy", target],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Mypy check failed:\n{r.stdout}\n{r.stderr}"
