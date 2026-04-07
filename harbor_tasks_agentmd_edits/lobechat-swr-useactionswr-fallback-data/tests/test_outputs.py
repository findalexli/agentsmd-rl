"""
Task: lobechat-swr-useactionswr-fallback-data
Repo: lobehub/lobe-chat @ 959c210e869803545d451c3019e178966188ef17
PR:   11514

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js ESM script with TypeScript type stripping."""
    script_path = Path(REPO) / "_eval_tmp.mts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            [
                "node",
                "--experimental-strip-types",
                "--no-warnings",
                str(script_path.name),
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- module loading sanity check
# ---------------------------------------------------------------------------


def test_swr_module_loads():
    """SWR module can be loaded and exports all expected hooks as functions."""
    result = _run_node(
        """
        import * as mod from './src/libs/swr/index.ts';

        const expected = [
            'useClientDataSWR',
            'useOnlyFetchOnceSWR',
            'useActionSWR',
        ];
        for (const name of expected) {
            if (!(name in mod)) {
                throw new Error(name + ' is not exported');
            }
            if (typeof mod[name] !== 'function') {
                throw new Error(
                    name + ' is not a function, got ' + typeof mod[name]
                );
            }
        }
        console.log('PASS');
        """
    )
    assert result.returncode == 0, f"Module load failed:\n{result.stderr}"
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------


def test_use_action_swr_uses_fallback_data():
    """useActionSWR uses useSWR with fallbackData, not useSWRMutation."""
    result = _run_node(
        """
        import * as mod from './src/libs/swr/index.ts';
        const src = mod.useActionSWR.toString();

        // Must NOT use useSWRMutation
        if (src.includes('useSWRMutation')) {
            throw new Error('useActionSWR still uses useSWRMutation');
        }

        // Must call useSWR
        if (!src.includes('useSWR')) {
            throw new Error('useActionSWR does not call useSWR');
        }

        // Must use fallbackData
        if (!src.includes('fallbackData')) {
            throw new Error('useActionSWR missing fallbackData');
        }

        // Must disable revalidateOnMount
        if (!src.includes('revalidateOnMount')) {
            throw new Error('useActionSWR missing revalidateOnMount');
        }

        console.log('PASS');
        """
    )
    assert result.returncode == 0, f"useActionSWR check failed:\n{result.stderr}"
    assert "PASS" in result.stdout


def test_swr_comments_english_only():
    """SWR module comments are in English, not Chinese."""
    swr_file = Path(REPO) / "src" / "libs" / "swr" / "index.ts"
    content = swr_file.read_text()

    # CJK Unified Ideographs range
    chinese_chars = [c for c in content if "\u4e00" <= c <= "\u9fff"]
    assert len(chinese_chars) == 0, (
        f"Found {len(chinese_chars)} Chinese characters in SWR module"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- config/documentation update tests
# ---------------------------------------------------------------------------


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
