"""
Task: lobechat-swr-useactionswr-fallback-data
Repo: lobehub/lobe-chat @ 959c210e869803545d451c3019e178966188ef17
PR:   11514

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/lobe-chat"


def test_swr_module_loads():
    """SWR module can be loaded and exports all expected hooks as functions."""
    swr_file = Path(REPO) / "src" / "libs" / "swr" / "index.ts"
    content = swr_file.read_text()

    # Check that expected hooks are exported
    expected_exports = [
        "export const useClientDataSWR",
        "export const useOnlyFetchOnceSWR",
        "export const useActionSWR",
    ]
    for export in expected_exports:
        assert export in content, f"Missing export: {export}"


def test_repo_swr_unit_tests():
    """Repo unit tests for SWR module pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && pnpm install --ignore-scripts >/dev/null 2>&1 && npx vitest run src/libs/swr/ --silent=passed-only"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"SWR unit tests failed:\n{r.stderr[-1000:]}"


def test_repo_swr_lint():
    """Repo ESLint passes on SWR module (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && pnpm install --ignore-scripts >/dev/null 2>&1 && npx eslint src/libs/swr/index.ts"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_swr_prettier():
    """Repo Prettier check passes on SWR module (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && pnpm install --ignore-scripts >/dev/null 2>&1 && npx prettier --check src/libs/swr/index.ts"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_use_action_swr_uses_fallback_data():
    """useActionSWR uses useSWR with fallbackData, not useSWRMutation."""
    swr_file = Path(REPO) / "src" / "libs" / "swr" / "index.ts"
    content = swr_file.read_text()

    # Extract useActionSWR function using regex
    match = re.search(r"export const useActionSWR[\s\S]*?(?=\nexport |\n// |\n\nexport |$)", content)
    assert match, "Could not find useActionSWR function"
    func_content = match.group(0)

    # Must NOT use useSWRMutation
    assert "useSWRMutation" not in func_content, "useActionSWR still uses useSWRMutation"

    # Must call useSWR
    assert "useSWR" in func_content, "useActionSWR does not call useSWR"

    # Must use fallbackData
    assert "fallbackData" in func_content, "useActionSWR missing fallbackData"

    # Must disable revalidateOnMount
    assert "revalidateOnMount" in func_content, "useActionSWR missing revalidateOnMount"


def test_swr_comments_english_only():
    """SWR module comments are in English, not Chinese."""
    swr_file = Path(REPO) / "src" / "libs" / "swr" / "index.ts"
    content = swr_file.read_text()

    # CJK Unified Ideographs range
    chinese_chars = [c for c in content if "\u4e00" <= c <= "\u9fff"]
    assert len(chinese_chars) == 0, (
        f"Found {len(chinese_chars)} Chinese characters in SWR module"
    )


def test_claude_md_references_linear_mdc():
    """CLAUDE.md references .cursor/rules/linear.mdc for Linear rules."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Should reference the external file
    assert ".cursor/rules/linear.mdc" in content, (
        "CLAUDE.md should reference .cursor/rules/linear.mdc"
    )

    # Should NOT have the full inline rules
    assert "Retrieve issue details" not in content, (
        "CLAUDE.md should not contain full inline Linear rules"
    )
    assert "Per-Issue Completion Rule" not in content, (
        "CLAUDE.md should not contain Per-Issue Completion Rule section"
    )


def test_linear_mdc_exists_with_rules():
    """File .cursor/rules/linear.mdc exists with Linear issue management rules."""
    linear_mdc = Path(REPO) / ".cursor" / "rules" / "linear.mdc"
    assert linear_mdc.exists(), ".cursor/rules/linear.mdc file must exist"

    content = linear_mdc.read_text()

    # Check for distinctive Linear rules content
    assert "alwaysApply: true" in content, (
        "linear.mdc should have alwaysApply frontmatter"
    )
    assert "Linear Issue Management" in content, (
        "linear.mdc should have Linear Issue Management heading"
    )
    assert "Completion Comment" in content, (
        "linear.mdc should have Completion Comment section"
    )
    assert "Per-Issue Completion Rule" in content, (
        "linear.mdc should have Per-Issue Completion Rule"
    )
    assert "In Review" in content, (
        "linear.mdc should mention In Review status"
    )
