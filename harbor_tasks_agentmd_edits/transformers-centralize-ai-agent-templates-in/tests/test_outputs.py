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
# Pass-to-pass (repo_tests) — CI checks that should pass on base commit
# ---------------------------------------------------------------------------

def test_repo_doc_toc():
    """Documentation TOC check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_doc_toc.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert r.returncode == 0, f"Doc TOC check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_dummies():
    """Dummy objects check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert r.returncode == 0, f"Dummies check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_inits():
    """Init files check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert r.returncode == 0, f"Inits check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_custom_init_isort():
    """Custom init isort check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/custom_init_isort.py", "--check_only"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert r.returncode == 0, f"Custom init isort check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_sort_auto_mappings():
    """Auto mappings sort check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/sort_auto_mappings.py", "--check_only"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert r.returncode == 0, f"Sort auto mappings check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_doctest_list():
    """Doctest list check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_doctest_list.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert r.returncode == 0, f"Doctest list check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


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


def test_make_clean_ai_removes_symlinks():
    """'make clean-ai' removes generated skill symlinks."""
    r = subprocess.run(["make", "clean-ai"], capture_output=True, cwd=REPO, timeout=30)
    assert r.returncode == 0, f"make clean-ai failed: {r.stderr.decode()[:500]}"

    assert not (Path(REPO) / ".claude" / "skills").exists(), \
        ".claude/skills should not exist after 'make clean-ai'"
    assert not (Path(REPO) / ".agents" / "skills").exists(), \
        ".agents/skills should not exist after 'make clean-ai'"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/doc file update tests
# ---------------------------------------------------------------------------

def test_ai_agents_md_content():
    """.ai/AGENTS.md contains required sections."""
    agents_md = Path(REPO) / ".ai" / "AGENTS.md"
    assert agents_md.exists(), ".ai/AGENTS.md must exist"

    content = agents_md.read_text()

    # Must preserve original policy content
    assert "Mandatory Agentic contribution policy" in content, \
        ".ai/AGENTS.md missing mandatory contribution policy section"
    assert "Copies and Modular Models" in content, \
        ".ai/AGENTS.md missing Copies and Modular Models section"

    # Must have new local agent setup instructions
    assert "make codex" in content or "make claude" in content, \
        ".ai/AGENTS.md should document the make codex/claude setup commands"


def test_ai_skills_type_checking_content():
    """.ai/skills/add-or-fix-type-checking/SKILL.md has required content."""
    skill_md = Path(REPO) / ".ai" / "skills" / "add-or-fix-type-checking" / "SKILL.md"
    assert skill_md.exists(), "SKILL.md must exist"

    content = skill_md.read_text()
    assert "ty check" in content, "SKILL.md should reference the 'ty check' command"
    assert "type-check" in content.lower() or "typing" in content.lower(), \
        "SKILL.md should describe type checking"
    # Must have frontmatter with name
    assert "name:" in content and "add-or-fix-type-checking" in content, \
        "SKILL.md should have proper frontmatter with name field"


def test_root_agents_md_symlink():
    """Root AGENTS.md is a symlink to .ai/AGENTS.md."""
    agents_md = Path(REPO) / "AGENTS.md"
    assert agents_md.is_symlink(), "AGENTS.md should be a symlink"

    target = os.readlink(str(agents_md))
    assert ".ai/AGENTS.md" in target, \
        f"AGENTS.md should point to .ai/AGENTS.md, got: {target}"

    # Symlink must resolve and have valid content
    content = agents_md.read_text()
    assert "Mandatory Agentic contribution policy" in content, \
        "AGENTS.md symlink does not resolve to valid content"


def test_root_claude_md_symlink():
    """Root CLAUDE.md is a symlink to .ai/AGENTS.md."""
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.is_symlink(), "CLAUDE.md should be a symlink"

    target = os.readlink(str(claude_md))
    assert ".ai/AGENTS.md" in target, \
        f"CLAUDE.md should point to .ai/AGENTS.md, got: {target}"

    # Symlink must resolve and have valid content
    content = claude_md.read_text()
    assert "Mandatory Agentic contribution policy" in content, \
        "CLAUDE.md symlink does not resolve to valid content"


def test_contributing_ai_section():
    """CONTRIBUTING.md documents AI agent setup."""
    contributing_md = Path(REPO) / "CONTRIBUTING.md"
    assert contributing_md.exists(), "CONTRIBUTING.md must exist"

    content = contributing_md.read_text()
    assert "ai agent" in content.lower(), \
        "CONTRIBUTING.md should have a section about AI agents"
    assert "make codex" in content or "make claude" in content, \
        "CONTRIBUTING.md should reference the make targets for agent setup"


def test_gitignore_excludes():
    """.gitignore excludes agent artifact directories."""
    gitignore = Path(REPO) / ".gitignore"
    assert gitignore.exists(), ".gitignore must exist"

    content = gitignore.read_text()
    assert ".agents/skills" in content, \
        ".gitignore should exclude .agents/skills"
    assert ".claude/skills" in content, \
        ".gitignore should exclude .claude/skills"
