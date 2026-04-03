"""
Task: transformers-centralize-ai-agent-templates-in
Repo: transformers @ 7cd2dd86ce3b2e598535f9aa1a40f79d6894f80a
PR:   huggingface/transformers#44489

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_makefile_syntax():
    """Makefile is syntactically valid and can be parsed by make."""
    r = subprocess.run(
        ["make", "-n", "style"],
        capture_output=True, cwd=REPO, timeout=30,
    )
    assert r.returncode == 0, f"Makefile parse error: {r.stderr.decode()[:500]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Makefile behavioral tests
# ---------------------------------------------------------------------------

def test_make_claude_creates_skills_symlink():
    """'make claude' must create .claude/skills as a symlink to ../.ai/skills."""
    # Clean up any prior state
    subprocess.run(["rm", "-rf", f"{REPO}/.claude/skills"], capture_output=True)

    r = subprocess.run(["make", "claude"], capture_output=True, cwd=REPO, timeout=30)
    assert r.returncode == 0, f"make claude failed: {r.stderr.decode()[:500]}"

    skills = Path(REPO) / ".claude" / "skills"
    assert skills.is_symlink(), ".claude/skills should be a symlink after 'make claude'"

    target = os.readlink(str(skills))
    assert ".ai/skills" in target, f".claude/skills should link to .ai/skills, got {target}"


def test_make_codex_creates_skills_symlink():
    """'make codex' must create .agents/skills as a symlink to ../.ai/skills."""
    subprocess.run(["rm", "-rf", f"{REPO}/.agents/skills"], capture_output=True)

    r = subprocess.run(["make", "codex"], capture_output=True, cwd=REPO, timeout=30)
    assert r.returncode == 0, f"make codex failed: {r.stderr.decode()[:500]}"

    skills = Path(REPO) / ".agents" / "skills"
    assert skills.is_symlink(), ".agents/skills should be a symlink after 'make codex'"

    target = os.readlink(str(skills))
    assert ".ai/skills" in target, f".agents/skills should link to .ai/skills, got {target}"



    r = subprocess.run(["make", "clean-ai"], capture_output=True, cwd=REPO, timeout=30)
    assert r.returncode == 0, f"make clean-ai failed: {r.stderr.decode()[:500]}"

    assert not (Path(REPO) / ".claude" / "skills").exists(), \
        ".claude/skills should not exist after 'make clean-ai'"
    assert not (Path(REPO) / ".agents" / "skills").exists(), \
        ".agents/skills should not exist after 'make clean-ai'"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/doc file update tests
# ---------------------------------------------------------------------------


    # Must preserve original policy content
    assert "Mandatory Agentic contribution policy" in content, \
        ".ai/AGENTS.md missing mandatory contribution policy section"
    assert "Copies and Modular Models" in content, \
        ".ai/AGENTS.md missing Copies and Modular Models section"

    # Must have new local agent setup instructions
    assert "make codex" in content or "make claude" in content, \
        ".ai/AGENTS.md should document the make codex/claude setup commands"



    content = skill_md.read_text()
    assert "ty check" in content, "SKILL.md should reference the 'ty check' command"
    assert "type-check" in content.lower() or "typing" in content.lower(), \
        "SKILL.md should describe type checking"
    # Must have frontmatter with name
    assert "name:" in content and "add-or-fix-type-checking" in content, \
        "SKILL.md should have proper frontmatter with name field"



    target = os.readlink(str(agents_md))
    assert ".ai/AGENTS.md" in target, \
        f"AGENTS.md should point to .ai/AGENTS.md, got: {target}"

    # Symlink must resolve and have valid content
    content = agents_md.read_text()
    assert "Mandatory Agentic contribution policy" in content, \
        "AGENTS.md symlink does not resolve to valid content"



    target = os.readlink(str(claude_md))
    assert ".ai/AGENTS.md" in target, \
        f"CLAUDE.md should point to .ai/AGENTS.md, got: {target}"

    # Symlink must resolve and have valid content
    content = claude_md.read_text()
    assert "Mandatory Agentic contribution policy" in content, \
        "CLAUDE.md symlink does not resolve to valid content"



    assert "ai agent" in content.lower(), \
        "CONTRIBUTING.md should have a section about AI agents"
    assert "make codex" in content or "make claude" in content, \
        "CONTRIBUTING.md should reference the make targets for agent setup"



    assert ".agents/skills" in content, \
        ".gitignore should exclude .agents/skills"
    assert ".claude/skills" in content, \
        ".gitignore should exclude .claude/skills"
