"""
Task: remix-add-supersede-pr-skill
Repo: remix-run/remix @ 64b3a160dc25bbb082b96673e12bb55935f3528d
PR:   11088

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/remix")
SCRIPT = REPO / "skills/supersede-pr/scripts/close_superseded_pr.ts"
AGENTS_MD = REPO / "AGENTS.md"
NODE_CMD = ["node", "--no-warnings", "--experimental-strip-types"]


def run_script(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        NODE_CMD + [str(SCRIPT)] + list(args),
        capture_output=True,
        text=True,
        timeout=10,
    )


# === Code behavior tests (fail-to-pass) ===


def test_help_shows_usage():
    """Script --help exits 0 and shows usage info with PR number placeholders."""
    result = run_script("--help")
    assert result.returncode == 0, f"Exit code {result.returncode}, stderr: {result.stderr}"
    output = result.stdout.lower()
    assert "usage" in output or "close_superseded_pr" in output, \
        f"Expected usage info, got: {result.stdout[:200]}"
    assert "old_pr" in output or "old pr" in output or "<old" in output, \
        "Usage should reference old_pr positional argument"


def test_requires_two_positional_args():
    """Script exits non-zero when called with fewer than 2 positional args."""
    result = run_script()
    assert result.returncode != 0, "Should fail with no args"
    result_one = run_script("100")
    assert result_one.returncode != 0, "Should fail with only one arg"


def test_rejects_non_numeric_pr():
    """Script rejects non-numeric PR numbers with a descriptive error."""
    result = run_script("abc", "123")
    assert result.returncode != 0, "Should reject non-numeric old_pr"
    combined = (result.stdout + result.stderr).lower()
    assert "numeric" in combined, f"Error should mention 'numeric', got: {combined[:200]}"

    result2 = run_script("100", "xyz")
    assert result2.returncode != 0
    combined2 = (result2.stdout + result2.stderr).lower()
    assert "numeric" in combined2


def test_rejects_same_pr_numbers():
    """Script rejects when old_pr and new_pr are the same number."""
    result = run_script("100", "100")
    assert result.returncode != 0, "Should reject identical PR numbers"
    combined = (result.stdout + result.stderr).lower()
    assert "different" in combined, f"Error should mention 'different', got: {combined[:200]}"


def test_rejects_unknown_arguments():
    """Script rejects unrecognized command-line flags."""
    result = run_script("100", "200", "--bogus")
    assert result.returncode != 0, "Should reject unknown flag --bogus"
    combined = (result.stdout + result.stderr).lower()
    assert "unknown" in combined, f"Error should mention 'unknown', got: {combined[:200]}"


# === Config/doc update tests (fail-to-pass) ===


def test_agents_md_documents_skills():
    """AGENTS.md must have a Skills section mentioning the supersede-pr skill."""
    content = AGENTS_MD.read_text().lower()
    assert "skill" in content, "AGENTS.md should mention skills"
    assert "supersede" in content, "AGENTS.md should document the supersede-pr skill"
    assert "supersede-pr" in content or "supersede_pr" in content, \
        "AGENTS.md should reference supersede-pr by name"


def test_agents_md_one_off_scripts_rule():
    """AGENTS.md must note that one-off scripts should be executable TypeScript."""
    content = AGENTS_MD.read_text().lower()
    assert "one-off" in content or "one off" in content, \
        "AGENTS.md should mention one-off scripts"
    assert "typescript" in content or "executable" in content, \
        "AGENTS.md should describe scripts as executable TypeScript"


# === Pass-to-pass ===


def test_existing_code_style_preserved():
    """Existing AGENTS.md code style rules remain intact after updates."""
    content = AGENTS_MD.read_text()
    assert "Prefer `let`" in content, "let/const rule should be preserved"
    assert "never use `var`" in content, "no-var rule should be preserved"
