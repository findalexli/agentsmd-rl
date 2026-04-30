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
        assert target == "AGENTS.md", f"CLAUDE.md symlink should point to AGENTS.md, got: {target}"


# [repo_tests] pass_to_pass
def test_repo_readme_symlink_valid():
    """README symlink should be valid at base commit (pass_to_pass)."""
    readme = Path(f"{REPO}/readme.md")
    assert readme.exists(), "readme.md symlink should resolve"
    assert readme.is_symlink(), "readme.md should be a symlink"
    target = os.readlink(readme)
    assert "packages/next/README.md" in target, f"Unexpected readme target: {target}"


# [repo_tests] pass_to_pass
def test_repo_no_broken_symlinks():
    """Repository should have no broken symlinks in tracked files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO} && find . -type l ! -exec test -e {{}} \; -print 2>/dev/null | grep -v '^\\./\\.git' | head -20"],
        capture_output=True, text=True, timeout=30,
    )
    broken_links = r.stdout.strip()
    if broken_links:
        non_node_modules = [l for l in broken_links.split('\n') if l and 'node_modules' not in l]
        if non_node_modules:
            raise AssertionError(f"Broken symlinks found: {non_node_modules}")


# [repo_tests] pass_to_pass
def test_repo_pnpm_config_valid():
    """pnpm package manager config should be valid (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO} && corepack enable && pnpm --version"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"pnpm config check failed: {r.stderr}"
    assert len(r.stdout.strip()) > 0, "pnpm version should be readable"


# [repo_tests] pass_to_pass
def test_repo_git_log_readable():
    """Git history should be readable (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    lines = r.stdout.strip().split('\n')
    assert len(lines) >= 1, f"Expected at least 1 commit, got {len(lines)}"


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
    assert "# Next.js Development Guide" in content, "AGENTS.md missing expected header"
    assert "Git Workflow" in content, "AGENTS.md missing Git Workflow section"


# [pr_diff] fail_to_pass
def test_claude_md_is_symlink():
    """CLAUDE.md should be a symbolic link pointing to AGENTS.md."""
    claude_md = Path(f"{REPO}/CLAUDE.md")

    assert claude_md.exists(), "CLAUDE.md does not exist"
    assert claude_md.is_symlink(), "CLAUDE.md should be a symbolic link"

    target = os.readlink(claude_md)
    assert target == "AGENTS.md", f"CLAUDE.md should point to AGENTS.md, got: {target}"

    agents_content = Path(f"{REPO}/AGENTS.md").read_text()
    claude_content = claude_md.read_text()
    assert agents_content == claude_content, "CLAUDE.md content does not match AGENTS.md"


# [pr_diff] fail_to_pass
def test_alexignore_updated():
    """.alexignore should include both AGENTS.md and CLAUDE.md."""
    alexignore = Path(f"{REPO}/.alexignore")
    assert alexignore.exists(), ".alexignore does not exist"

    content = alexignore.read_text()

    assert "AGENTS.md" in content, ".alexignore missing AGENTS.md"
    assert "CLAUDE.md" in content, ".alexignore missing CLAUDE.md"


# [pr_diff] fail_to_pass
def test_symlink_resolves_correctly():
    """The CLAUDE.md symlink should resolve and be readable via subprocess."""
    r = subprocess.run(
        ["readlink", f"{REPO}/CLAUDE.md"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"CLAUDE.md is not a symlink (readlink failed): {r.stderr}"
    assert r.stdout.strip() == "AGENTS.md", f"Unexpected symlink target: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_agents_md_has_content():
    """AGENTS.md should have substantial content from the original CLAUDE.md."""
    agents_md = Path(f"{REPO}/AGENTS.md")
    content = agents_md.read_text()

    assert "Build Commands" in content, "Missing Build Commands section"
    assert "Testing" in content, "Missing Testing section"
    assert "Linting and Types" in content, "Missing Linting and Types section"

    assert len(content) > 5000, f"AGENTS.md content too short ({len(content)} chars), expected substantial content"


# ---------------------------------------------------------------------------
# CI-mined test (scoped — verifies .alexignore works with the alex linter)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_alex_ignores_configured_files():
    """CI: alex linter should respect .alexignore entries (pass_to_pass)."""
    r = subprocess.run(
        ["alex", f"{REPO}/CLAUDE.md"],
        capture_output=True, text=True, timeout=60,
    )
    combined = (r.stdout + r.stderr).lower()
    # alex should report the file as "ignored" when it's in .alexignore.
    # CLAUDE.md is in .alexignore at both base and gold.
    assert "ignored" in combined, f"alex did not report CLAUDE.md as ignored: {combined[:500]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_wasm_pnpm():
    """pass_to_pass | CI job 'build-wasm' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm install'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_wasm_pnpm_2():
    """pass_to_pass | CI job 'build-wasm' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_docs_links_run_link_checker():
    """pass_to_pass | CI job 'validate-docs-links' → step 'Run link checker'"""
    r = subprocess.run(
        ["bash", "-lc", 'node ./.github/actions/validate-docs-links/dist/index.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run link checker' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")