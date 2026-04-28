"""Structural checks for the make-pr skill markdown authoring task."""

import subprocess

REPO = "/workspace/remix"


def test_make_pr_skill_file_exists():
    """Skills/make-pr/SKILL.md was created with correct frontmatter."""
    r = subprocess.run(
        ["grep", "-c", "name: make-pr", f"{REPO}/skills/make-pr/SKILL.md"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"skills/make-pr/SKILL.md missing or lacks 'name: make-pr'"


def test_agents_md_references_make_pr():
    """AGENTS.md lists the make-pr skill with a description and file path."""
    r = subprocess.run(
        ["grep", "-c", "make-pr.*Create GitHub pull requests", f"{REPO}/AGENTS.md"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, "AGENTS.md missing make-pr skill reference"


def test_openai_config_exists():
    """Skills/make-pr/agents/openai.yaml was created with display name."""
    r = subprocess.run(
        ["grep", "-c", "Make PR", f"{REPO}/skills/make-pr/agents/openai.yaml"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, "skills/make-pr/agents/openai.yaml missing or lacks 'Make PR'"


def test_supersede_pr_skill_intact():
    """Existing supersede-pr skill was not damaged by the changes."""
    r = subprocess.run(
        ["grep", "-c", "name: supersede-pr", f"{REPO}/skills/supersede-pr/SKILL.md"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, "supersede-pr SKILL.md was accidentally modified or removed"
