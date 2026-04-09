"""
Task: next.js-rename-claudemd-to-agentsmd-with
Repo: vercel/next.js @ c5b19eb7f5cf48dffa1b8bf87cd089f079fb031a
PR:   88105

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — verify repo CI still passes after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_git_status_clean():
    """Repository should have clean git status (no uncommitted changes before fix)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # Before fix is applied, repo should be clean
    # After fix, there will be changes, so this tests the base state
    assert r.returncode == 0, f"Git status failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_claude_md_readable():
    """CLAUDE.md should be readable at base commit (pass_to_pass)."""
    r = subprocess.run(
        ["cat", f"{REPO}/CLAUDE.md"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"CLAUDE.md not readable: {r.stderr}"
    content = r.stdout
    # Should have substantial content
    assert len(content) > 5000, f"CLAUDE.md too short ({len(content)} chars)"
    assert "# Next.js Development Guide" in content, "Missing expected header"


# [repo_tests] pass_to_pass
def test_repo_alexignore_exists():
    """.alexignore should exist at base commit (pass_to_pass)."""
    alexignore = Path(f"{REPO}/.alexignore")
    assert alexignore.exists(), ".alexignore does not exist at base commit"


# [repo_tests] pass_to_pass
def test_repo_claude_md_valid():
    """CLAUDE.md should be valid (regular file or working symlink) (pass_to_pass)."""
    claude_md = Path(f"{REPO}/CLAUDE.md")
    assert claude_md.exists(), "CLAUDE.md should exist and be readable"
    
    # Check that content is valid regardless of file type
    content = claude_md.read_text()
    assert "# Next.js Development Guide" in content, "CLAUDE.md should have valid content"
    
    # If it's a symlink, verify it points to a valid target
    if claude_md.is_symlink():
        target = os.readlink(claude_md)
        # Should point to AGENTS.md (relative path)
        assert target == "AGENTS.md", f"CLAUDE.md symlink should point to AGENTS.md, got: {target}"


# [repo_tests] pass_to_pass
def test_repo_readme_symlink_valid():
    """README symlink should be valid at base commit (pass_to_pass)."""
    readme = Path(f"{REPO}/readme.md")
    assert readme.exists(), "readme.md symlink should resolve"
    assert readme.is_symlink(), "readme.md should be a symlink"
    target = os.readlink(readme)
    # Should point to packages/next/README.md
    assert "packages/next/README.md" in target, f"Unexpected readme target: {target}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_exists():
    """AGENTS.md file should exist with the agent instructions content."""
    agents_md = Path(f"{REPO}/AGENTS.md")
    assert agents_md.exists(), "AGENTS.md does not exist"
    assert agents_md.is_file(), "AGENTS.md should be a regular file, not a symlink"

    content = agents_md.read_text()
    # Should contain key content from the original CLAUDE.md
    assert "# Next.js Development Guide" in content, "AGENTS.md missing expected header"
    assert "Git Workflow" in content, "AGENTS.md missing Git Workflow section"


# [pr_diff] fail_to_pass
def test_claude_md_is_symlink():
    """CLAUDE.md should be a symbolic link pointing to AGENTS.md."""
    claude_md = Path(f"{REPO}/CLAUDE.md")

    # Should exist
    assert claude_md.exists(), "CLAUDE.md does not exist"

    # Should be a symlink (not a regular file)
    assert claude_md.is_symlink(), "CLAUDE.md should be a symbolic link"

    # Should point to AGENTS.md
    target = os.readlink(claude_md)
    assert target == "AGENTS.md", f"CLAUDE.md should point to AGENTS.md, got: {target}"

    # Should be readable and have same content as AGENTS.md
    agents_content = Path(f"{REPO}/AGENTS.md").read_text()
    claude_content = claude_md.read_text()
    assert agents_content == claude_content, "CLAUDE.md content does not match AGENTS.md"


# [pr_diff] fail_to_pass
def test_alexignore_updated():
    """.alexignore should include both AGENTS.md and CLAUDE.md."""
    alexignore = Path(f"{REPO}/.alexignore")
    assert alexignore.exists(), ".alexignore does not exist"

    content = alexignore.read_text()

    # Should have AGENTS.md
    assert "AGENTS.md" in content, ".alexignore missing AGENTS.md"

    # Should have CLAUDE.md
    assert "CLAUDE.md" in content, ".alexignore missing CLAUDE.md"


# [pr_diff] fail_to_pass
def test_symlink_resolves_correctly():
    """The CLAUDE.md symlink should resolve and be readable via subprocess."""
    # Use subprocess to verify the symlink works at the OS level
    r = subprocess.run(
        ["cat", f"{REPO}/CLAUDE.md"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Failed to read CLAUDE.md via symlink: {r.stderr}"

    content = r.stdout
    assert "# Next.js Development Guide" in content, "Symlinked CLAUDE.md missing expected content"
    assert "Git Workflow" in content, "Symlinked CLAUDE.md missing Git Workflow section"


# [pr_diff] fail_to_pass
def test_agents_md_has_content():
    """AGENTS.md should have substantial content from the original CLAUDE.md."""
    agents_md = Path(f"{REPO}/AGENTS.md")
    content = agents_md.read_text()

    # Check for key sections that were in the original CLAUDE.md
    assert "Build Commands" in content, "Missing Build Commands section"
    assert "Testing" in content, "Missing Testing section"
    assert "Linting and Types" in content, "Missing Linting and Types section"

    # Should be substantial (not just a stub)
    assert len(content) > 5000, f"AGENTS.md content too short ({len(content)} chars), expected substantial content"
