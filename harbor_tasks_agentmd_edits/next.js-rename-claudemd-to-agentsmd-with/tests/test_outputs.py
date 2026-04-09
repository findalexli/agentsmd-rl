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
