"""
Task: electric-add-claude-code-review-agent
Repo: electric-sql/electric @ 7ba32193cc9f970835acdcb2de48101f1a812ae9
PR: 3819

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/electric"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_claude_md_exists():
    """CLAUDE.md file is created with correct content linking to AGENTS.md."""
    claude_md = Path(f"{REPO}/CLAUDE.md")
    assert claude_md.exists(), "CLAUDE.md does not exist"

    content = claude_md.read_text()
    assert "# Claude Code Guidelines" in content, "CLAUDE.md missing expected header"
    assert "AGENTS.md" in content, "CLAUDE.md should reference AGENTS.md"


def test_pr_review_command_exists():
    """.claude/commands/pr-review.md contains the 5-phase review process."""
    pr_review = Path(f"{REPO}/.claude/commands/pr-review.md")
    assert pr_review.exists(), ".claude/commands/pr-review.md does not exist"

    content = pr_review.read_text()
    # Verify it contains the 5 phases
    assert "## Phase 1: Gather Context" in content, "Missing Phase 1"
    assert "## Phase 2: Analyze Changes" in content, "Missing Phase 2"
    assert "## Phase 3: Iteration Awareness" in content, "Missing Phase 3"
    assert "## Phase 4: Compose Review" in content, "Missing Phase 4"
    assert "## Phase 5: Post Review" in content, "Missing Phase 5"
    # Verify it has Electric-specific criteria
    assert "Elixir/OTP" in content or "Elixir" in content, "Missing Elixir conventions"


def test_workflow_label_trigger_exists():
    """.github/workflows/claude-code-review.yml workflow for label-triggered reviews exists."""
    workflow = Path(f"{REPO}/.github/workflows/claude-code-review.yml")
    assert workflow.exists(), "claude-code-review.yml does not exist"

    content = workflow.read_text()
    # Verify trigger conditions
    assert "labeled" in content, "Missing 'labeled' trigger"
    assert "synchronize" in content, "Missing 'synchronize' trigger"
    assert "claude" in content, "Missing 'claude' label reference"
    # Verify it uses the action
    assert "anthropics/claude-code-action@v1" in content, "Missing claude-code-action"
    # Verify it references the pr-review command
    assert "pr-review.md" in content, "Missing reference to pr-review.md"


def test_workflow_mention_trigger_exists():
    """.github/workflows/claude.yml workflow for @claude mentions exists."""
    workflow = Path(f"{REPO}/.github/workflows/claude.yml")
    assert workflow.exists(), "claude.yml does not exist"

    content = workflow.read_text()
    # Verify trigger on @claude mention
    assert "@claude" in content, "Missing @claude mention trigger"
    assert "issue_comment" in content, "Missing issue_comment trigger"
    assert "anthropics/claude-code-action@v1" in content, "Missing claude-code-action"


def test_gitignore_updated():
    """.gitignore changed from .claude to .claude/settings.local.json."""
    gitignore = Path(f"{REPO}/.gitignore")
    assert gitignore.exists(), ".gitignore does not exist"

    content = gitignore.read_text()
    # Should NOT have the old pattern
    assert "\n.claude\n" not in content and content != ".claude" and not content.endswith("\n.claude"), \
        ".gitignore still contains '.claude' (should be .claude/settings.local.json)"
    # Should have the new pattern
    assert ".claude/settings.local.json" in content, "Missing .claude/settings.local.json in .gitignore"


def test_claude_md_links_agents_md():
    """CLAUDE.md correctly links to AGENTS.md as per project conventions."""
    claude_md = Path(f"{REPO}/CLAUDE.md")
    assert claude_md.exists(), "CLAUDE.md does not exist"

    content = claude_md.read_text()
    # Verify the link pattern (either [AGENTS.md] or [./AGENTS.md])
    assert re.search(r'\[AGENTS\.md\]|\[\.\/AGENTS\.md\]|\.\/AGENTS\.md', content), \
        "CLAUDE.md should link to AGENTS.md"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — syntax checks
# -----------------------------------------------------------------------------

def test_yaml_syntax_valid():
    """Workflow YAML files have valid syntax."""
    workflow1 = Path(f"{REPO}/.github/workflows/claude-code-review.yml")
    workflow2 = Path(f"{REPO}/.github/workflows/claude.yml")

    assert workflow1.exists(), "claude-code-review.yml does not exist"
    assert workflow2.exists(), "claude.yml does not exist"

    # Validate YAML syntax using yamllint
    r1 = subprocess.run(
        ["yamllint", "-d", "relaxed", str(workflow1)],
        capture_output=True, text=True, timeout=30,
    )
    r2 = subprocess.run(
        ["yamllint", "-d", "relaxed", str(workflow2)],
        capture_output=True, text=True, timeout=30,
    )

    assert r1.returncode == 0, f"claude-code-review.yml YAML syntax error: {r1.stdout}"
    assert r2.returncode == 0, f"claude.yml YAML syntax error: {r2.stdout}"


def test_markdown_files_valid():
    """Markdown command files have valid structure."""
    pr_review = Path(f"{REPO}/.claude/commands/pr-review.md")
    claude_md = Path(f"{REPO}/CLAUDE.md")

    assert pr_review.exists(), ".claude/commands/pr-review.md does not exist"
    assert claude_md.exists(), "CLAUDE.md does not exist"

    # Check for basic markdown validity (has headers, not empty)
    pr_content = pr_review.read_text()
    claude_content = claude_md.read_text()

    assert len(pr_content) > 1000, "pr-review.md seems too short"
    assert len(claude_content) > 10, "CLAUDE.md seems too short"

    # Verify markdown headers exist
    assert re.search(r'^#+ ', pr_content, re.MULTILINE), "pr-review.md missing markdown headers"
    assert re.search(r'^#+ ', claude_content, re.MULTILINE), "CLAUDE.md missing markdown headers"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI validation tests
# -----------------------------------------------------------------------------

def test_repo_pr_workflow_yaml_valid():
    """New PR workflow YAML has valid syntax (pass_to_pass)."""
    workflow = Path(f"{REPO}/.github/workflows/claude-code-review.yml")
    assert workflow.exists(), "claude-code-review.yml does not exist"

    r = subprocess.run(
        ["yamllint", "-d", "relaxed", str(workflow)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"claude-code-review.yml YAML syntax error: {r.stdout}"


def test_repo_mention_workflow_yaml_valid():
    """New mention workflow YAML has valid syntax (pass_to_pass)."""
    workflow = Path(f"{REPO}/.github/workflows/claude.yml")
    assert workflow.exists(), "claude.yml does not exist"

    r = subprocess.run(
        ["yamllint", "-d", "relaxed", str(workflow)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"claude.yml YAML syntax error: {r.stdout}"
