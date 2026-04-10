"""
Task: next.js-chore-add-claude-code-configuration
Repo: vercel/next.js @ c74cb2ae25bbe515c600b85f1e974f7eb26db576
PR:   87943

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_exists_with_content():
    """CLAUDE.md created with Next.js development guide content."""
    claude_md = Path(f"{REPO}/CLAUDE.md")
    assert claude_md.exists(), "CLAUDE.md does not exist"

    content = claude_md.read_text()
    # Verify key sections from the PR are present
    assert "# Next.js Development Guide" in content, "Missing header"
    assert "## Git Workflow" in content, "Missing Git Workflow section"
    assert "gt create" in content, "Missing gt create command"
    assert "gt submit --no-edit" in content, "Missing gt submit --no-edit command"
    assert "## Build Commands" in content, "Missing Build Commands section"
    assert "## Testing" in content, "Missing Testing section"


# [pr_diff] fail_to_pass
def test_claude_ci_failures_command_exists():
    """.claude/commands/ci-failures.md created with CI analysis instructions."""
    ci_failures = Path(f"{REPO}/.claude/commands/ci-failures.md")
    assert ci_failures.exists(), ".claude/commands/ci-failures.md does not exist"

    content = ci_failures.read_text()
    # Verify key CI analysis content from PR is present
    assert "# Check CI Failures" in content, "Missing header"
    assert "gh api" in content, "Missing gh api usage for CI logs"
    assert "in_progress" in content, "Missing in_progress run handling"
    assert "Parallel subagent" in content or "subagent" in content, "Missing subagent mention"


# [pr_diff] fail_to_pass
def test_gitignore_updated_for_claude():
    """.gitignore updated to ignore Claude Code local settings."""
    gitignore = Path(f"{REPO}/.gitignore")
    assert gitignore.exists(), ".gitignore does not exist"

    content = gitignore.read_text()
    # Verify Claude Code ignores added
    assert ".claude/settings.local.json" in content, "Missing .claude/settings.local.json ignore"
    assert ".claude/plans/" in content, "Missing .claude/plans/ ignore"
    assert ".claude/todos.json" in content, "Missing .claude/todos.json ignore"
    assert "CLAUDE.local.md" in content, "Missing CLAUDE.local.md ignore"


# [pr_diff] fail_to_pass
def test_alexignore_updated_for_claude():
    """.alexignore updated to ignore .claude/ directory and CLAUDE.md."""
    alexignore = Path(f"{REPO}/.alexignore")
    assert alexignore.exists(), ".alexignore does not exist"

    content = alexignore.read_text()
    # Verify alex additions for Claude Code
    assert ".claude/" in content, "Missing .claude/ ignore"
    assert "CLAUDE.md" in content, "Missing CLAUDE.md ignore"


# [pr_diff] fail_to_pass
def test_claude_md_has_graphite_safety_rules():
    """CLAUDE.md contains Graphite stack safety rules."""
    claude_md = Path(f"{REPO}/CLAUDE.md")
    assert claude_md.exists(), "CLAUDE.md does not exist"

    content = claude_md.read_text()
    # Verify Graphite-specific safety content
    assert "Graphite Stack Safety Rules" in content, "Missing Graphite Stack Safety Rules"
    assert "Never use `git stash` with Graphite" in content, "Missing git stash warning"
    assert "gt checkout" in content, "Missing gt checkout reference"
    assert "gt modify" in content, "Missing gt modify reference"


# [pr_diff] fail_to_pass
def test_claude_md_has_testing_commands():
    """CLAUDE.md contains testing commands section with pnpm test commands."""
    claude_md = Path(f"{REPO}/CLAUDE.md")
    assert claude_md.exists(), "CLAUDE.md does not exist"

    content = claude_md.read_text()
    # Verify testing section has specific commands
    assert "pnpm test-dev-turbo" in content, "Missing pnpm test-dev-turbo command"
    assert "pnpm test-start-turbo" in content, "Missing pnpm test-start-turbo command"
    assert "pnpm test-unit" in content, "Missing pnpm test-unit command"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — real CI commands that should pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_git_status_clean():
    """Repo has no uncommitted changes (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Only check for actual file changes, ignore untracked files
    lines = [line for line in r.stdout.strip().split("\n") if line and not line.startswith("??")]
    assert len(lines) == 0, f"Repo has uncommitted changes:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_prettier_package_json():
    """Repo's package.json files are properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "package.json", "pnpm-workspace.yaml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_alex_lint():
    """Repo's markdown files pass alex linting (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "alex", "."], capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # alex returns 0 on success (warnings don't fail the command, only errors do)
    assert r.returncode == 0, f"Alex lint failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub and structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_claude_md_not_empty():
    """CLAUDE.md is not empty or stub."""
    claude_md = Path(f"{REPO}/CLAUDE.md")
    assert claude_md.exists(), "CLAUDE.md does not exist"

    content = claude_md.read_text().strip()
    assert len(content) > 1000, "CLAUDE.md is too short/empty (likely stub)"
    # Should have multiple sections
    assert content.count("## ") >= 3, "CLAUDE.md missing expected sections"


# [static] pass_to_pass
def test_ci_failures_md_not_empty():
    """.claude/commands/ci-failures.md is not empty or stub."""
    ci_failures = Path(f"{REPO}/.claude/commands/ci-failures.md")
    assert ci_failures.exists(), ".claude/commands/ci-failures.md does not exist"

    content = ci_failures.read_text().strip()
    assert len(content) > 2000, "ci-failures.md is too short/empty (likely stub)"
    # Should have multiple sections with commands
    assert "```bash" in content, "ci-failures.md missing bash code blocks"
    assert content.count("```") >= 4, "ci-failures.md missing expected code blocks"


# [static] pass_to_pass
def test_claude_directory_structure_correct():
    """.claude/ directory exists with correct structure."""
    claude_dir = Path(f"{REPO}/.claude")
    commands_dir = Path(f"{REPO}/.claude/commands")

    assert claude_dir.exists(), ".claude/ directory does not exist"
    assert commands_dir.exists(), ".claude/commands/ directory does not exist"

    # Verify the expected file is there
    assert (commands_dir / "ci-failures.md").exists(), "ci-failures.md not in commands/"
