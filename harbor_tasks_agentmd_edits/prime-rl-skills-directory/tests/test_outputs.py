"""
Task: prime-rl-skills-directory
Repo: PrimeIntellect-ai/prime-rl @ 31b48b8b10db390d835909a6fd976f29d9880c81
PR:   1747

This task requires both structural changes (skills directory + symlink) and
documentation updates (AGENTS.md describing the skills system).

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path
import os

REPO = "/workspace/prime-rl"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural checks
# ---------------------------------------------------------------------------

def test_agents_md_exists():
    """AGENTS.md must exist and be readable."""
    agents_md = Path(REPO) / "AGENTS.md"
    assert agents_md.exists(), "AGENTS.md must exist"
    content = agents_md.read_text()
    assert len(content) > 0, "AGENTS.md must not be empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — skills directory structure tests
# ---------------------------------------------------------------------------

def test_skills_directory_exists():
    """skills/ directory must exist with proper structure."""
    skills_dir = Path(REPO) / "skills"
    assert skills_dir.exists(), "skills/ directory must exist"
    assert skills_dir.is_dir(), "skills/ must be a directory"


def test_inference_server_skill_exists():
    """skills/inference-server/SKILL.md must exist with proper content."""
    skill_file = Path(REPO) / "skills" / "inference-server" / "SKILL.md"
    assert skill_file.exists(), "skills/inference-server/SKILL.md must exist"

    content = skill_file.read_text()
    # Check for frontmatter markers
    assert "---" in content, "SKILL.md must have YAML frontmatter"
    # Check for required content sections
    assert "inference-server" in content, "Must reference inference-server skill name"
    assert "vllm" in content.lower() or "vLLM" in content, "Must mention vLLM"
    assert "entry point" in content.lower() or "uv run inference" in content, \
        "Must document the inference entry point"


def test_toml_config_skill_exists():
    """skills/toml-config/SKILL.md must exist with proper content."""
    skill_file = Path(REPO) / "skills" / "toml-config" / "SKILL.md"
    assert skill_file.exists(), "skills/toml-config/SKILL.md must exist"

    content = skill_file.read_text()
    # Check for frontmatter markers
    assert "---" in content, "SKILL.md must have YAML frontmatter"
    # Check for required content sections
    assert "toml-config" in content, "Must reference toml-config skill name"
    assert "TOML" in content, "Must mention TOML"
    assert "@" in content, "Must document the @ config syntax"


def test_claude_skills_symlink_exists():
    """.claude/skills symlink must point to ../skills."""
    claude_skills = Path(REPO) / ".claude" / "skills"
    assert claude_skills.exists() or claude_skills.is_symlink(), \
        ".claude/skills symlink must exist"

    # Check it's a symlink pointing to the right place
    if claude_skills.is_symlink():
        target = os.readlink(claude_skills)
        assert "skills" in target, f".claude/skills must point to skills/, got: {target}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — AGENTS.md documentation update tests
# ---------------------------------------------------------------------------

def test_agents_md_documents_skills_section():
    """AGENTS.md must have a Skills section documenting the skills system."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Check for Skills section header
    assert "## Skills" in content, "AGENTS.md must have a ## Skills section"
    # Check for key concepts
    assert "skills/" in content, "Must reference skills/ directory"
    assert ".claude/skills" in content, "Must reference .claude/skills symlink"


def test_agents_md_documents_skill_maintenance():
    """AGENTS.md must explain skill maintenance responsibilities."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Check for maintenance guidance
    assert "maintaining" in content.lower() or "maintain" in content.lower(), \
        "Must mention skill maintenance"
    # Check for explicit agent responsibility
    assert "you are responsible" in content.lower() or "responsible for" in content.lower(), \
        "Must state agent responsibility for maintaining skills"


def test_agents_md_references_toml_config_skill():
    """AGENTS.md must reference the toml-config skill for CLI usage."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Check that CLI usage section points to skills
    assert "toml-config" in content, "AGENTS.md must reference toml-config skill"
    assert "skills/" in content, "Must reference skills/ directory for config details"
