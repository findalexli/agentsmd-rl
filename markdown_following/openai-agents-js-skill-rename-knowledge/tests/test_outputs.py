"""Structural verification tests for agent markdown edits.

These tests check that the agent correctly renamed the verify-changes skill,
added the openai-knowledge skill, and updated AGENTS.md accordingly.
"""

import os
import subprocess

REPO = "/workspace/openai-agents-js"


def test_agents_md_has_code_change_verification_section():
    """AGENTS.md has a ### `$code-change-verification` subsection."""
    path = os.path.join(REPO, "AGENTS.md")
    with open(path) as f:
        content = f.read()
    assert "### `$code-change-verification`" in content, \
        "AGENTS.md missing code-change-verification subsection heading"


def test_agents_md_has_openai_knowledge_section():
    """AGENTS.md has a ### `$openai-knowledge` subsection."""
    path = os.path.join(REPO, "AGENTS.md")
    with open(path) as f:
        content = f.read()
    assert "### `$openai-knowledge`" in content, \
        "AGENTS.md missing openai-knowledge subsection heading"


def test_agents_md_describes_skip_rules():
    """AGENTS.md describes when code-change-verification can be skipped."""
    path = os.path.join(REPO, "AGENTS.md")
    with open(path) as f:
        content = f.read()
    assert "skip" in content.lower(), \
        "AGENTS.md does not mention skip conditions"
    assert "docs-only" in content or "repo-meta" in content, \
        "AGENTS.md missing docs-only or repo-meta skip criteria"
    assert "when changes affect runtime code" in content, \
        "AGENTS.md missing conditional trigger description"


def test_agents_md_no_stale_verify_changes_refs():
    """AGENTS.md no longer has stale $verify-changes references."""
    r = subprocess.run(
        ["grep", "-c", "verify-changes", os.path.join(REPO, "AGENTS.md")],
        capture_output=True, text=True
    )
    # After the fix, verify-changes should not appear in AGENTS.md
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count == 0, f"AGENTS.md still has {count} verify-changes reference(s)"


def test_code_change_verification_skill_exists():
    """.codex/skills/code-change-verification/SKILL.md exists with correct frontmatter."""
    path = os.path.join(REPO, ".codex/skills/code-change-verification/SKILL.md")
    assert os.path.isfile(path), f"Missing: {path}"
    with open(path) as f:
        content = f.read()
    assert "name: code-change-verification" in content, \
        "SKILL.md frontmatter missing name: code-change-verification"


def test_openai_knowledge_skill_exists():
    """.codex/skills/openai-knowledge/SKILL.md exists with correct frontmatter."""
    path = os.path.join(REPO, ".codex/skills/openai-knowledge/SKILL.md")
    assert os.path.isfile(path), f"Missing: {path}"
    with open(path) as f:
        content = f.read()
    assert "name: openai-knowledge" in content, \
        "SKILL.md frontmatter missing name: openai-knowledge"
    assert "openaiDeveloperDocs" in content, \
        "SKILL.md missing openaiDeveloperDocs MCP server reference"


def test_old_skill_directory_removed():
    """Old .codex/skills/verify-changes/ no longer exists."""
    path = os.path.join(REPO, ".codex/skills/verify-changes")
    assert not os.path.exists(path), \
        f"Old skill directory still exists: {path}"


def test_scripts_use_new_name():
    """Verification scripts echo the new skill name."""
    scripts = [
        ".codex/skills/code-change-verification/scripts/run.sh",
        ".codex/skills/code-change-verification/scripts/run.ps1",
    ]
    for script in scripts:
        path = os.path.join(REPO, script)
        assert os.path.isfile(path), f"Missing: {path}"
        with open(path) as f:
            content = f.read()
        assert "code-change-verification" in content, \
            f"{script} does not reference code-change-verification"


def test_repo_structure_intact():
    """Repo root still has expected top-level files (pass_to_pass)."""
    required = ["AGENTS.md", "package.json", "README.md"]
    for fname in required:
        path = os.path.join(REPO, fname)
        assert os.path.isfile(path), f"Missing top-level file: {fname}"
    # Verify some shell script is valid bash (check whichever exists)
    for candidate in [
        ".codex/skills/code-change-verification/scripts/run.sh",
        ".codex/skills/verify-changes/scripts/run.sh",
    ]:
        path = os.path.join(REPO, candidate)
        if os.path.isfile(path):
            r = subprocess.run(
                ["bash", "-n", path],
                capture_output=True, text=True
            )
            assert r.returncode == 0, f"{candidate} syntax error:\n{r.stderr}"
            break
    else:
        assert False, "No run.sh found to validate"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check_generated_declarations():
    """pass_to_pass | CI job 'test' → step 'Check generated declarations'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r -F "@openai/*" dist:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated declarations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_type_check_docs_scripts():
    """pass_to_pass | CI job 'test' → step 'Type-check docs scripts'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docs:scripts:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type-check docs scripts' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")