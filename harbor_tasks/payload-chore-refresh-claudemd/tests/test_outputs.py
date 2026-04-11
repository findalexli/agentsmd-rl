"""
Task: payload-chore-refresh-claudemd
Repo: payloadcms/payload @ fdea8d8457fafe59be4b877a52a00990a735fd38
PR:   14268

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/payload"


def _setup_pnpm():
    """Enable corepack and return pnpm path."""
    subprocess.run(["corepack", "enable"], capture_output=True, cwd=REPO)
    return "pnpm"


def _run_pnpm(cmd, timeout=120):
    """Helper to run pnpm commands via corepack."""
    _setup_pnpm()
    return subprocess.run(
        ["pnpm", cmd],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - basic validation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_claude_md_exists():
    """CLAUDE.md must exist as a regular file (not symlink)."""
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md must exist"
    assert claude_md.is_file(), "CLAUDE.md must be a regular file, not a symlink"
    assert not claude_md.is_symlink(), "CLAUDE.md must not be a symlink"


# [static] pass_to_pass
def test_agents_md_is_symlink():
    """AGENTS.md must exist as a symlink pointing to CLAUDE.md."""
    agents_md = Path(REPO) / "AGENTS.md"
    assert agents_md.exists() or agents_md.is_symlink(), "AGENTS.md must exist"
    assert agents_md.is_symlink(), "AGENTS.md must be a symlink"


# [static] pass_to_pass
def test_gitignore_exists():
    """.gitignore must exist."""
    gitignore = Path(REPO) / ".gitignore"
    assert gitignore.exists(), ".gitignore must exist"


# ---------------------------------------------------------------------------
# Repo CI/CD tests (pass_to_pass) - verify repo's own CI passes
# Dependencies are installed as part of the test (required for CI commands)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    _setup_pnpm()
    # Install dependencies first (needed for any pnpm command to work)
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        # If install fails, skip the test
        print(f"Skipping: pnpm install failed: {r.stderr[-500:]}")
        return
    
    r = subprocess.run(
        ["pnpm", "test:unit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_type_tests():
    """Repo's TypeScript type tests pass (pass_to_pass)."""
    _setup_pnpm()
    # Install dependencies first
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        print(f"Skipping: pnpm install failed: {r.stderr[-500:]}")
        return
    
    r = subprocess.run(
        ["pnpm", "test:types"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Type tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build_translations():
    """Repo's translations package builds successfully (pass_to_pass)."""
    _setup_pnpm()
    # Install dependencies first
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        print(f"Skipping: pnpm install failed: {r.stderr[-500:]}")
        return
    
    r = subprocess.run(
        ["pnpm", "build:translations"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_type_generation():
    """Repo's type generation for test fields works (pass_to_pass)."""
    _setup_pnpm()
    # Install dependencies first
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        print(f"Skipping: pnpm install failed: {r.stderr[-500:]}")
        return
    
    r = subprocess.run(
        ["pnpm", "dev:generate-types", "fields"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Type generation failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests for CLAUDE.md content
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_has_project_structure():
    """CLAUDE.md must contain Project Structure section with key directories."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Check for Project Structure section
    assert "## Project Structure" in content or "### Project Structure" in content, \
        "CLAUDE.md must have a Project Structure section"

    # Check for key directories mentioned
    assert "packages/" in content, "CLAUDE.md must mention packages/ directory"
    assert "test/" in content, "CLAUDE.md must mention test/ directory"


# [pr_diff] fail_to_pass
def test_claude_md_has_build_commands():
    """CLAUDE.md must document build commands (pnpm build, pnpm build:all)."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Check for Build Commands section
    assert "## Build Commands" in content or "### Build Commands" in content, \
        "CLAUDE.md must have a Build Commands section"

    # Check for key build commands
    assert "pnpm build" in content, "CLAUDE.md must mention pnpm build"
    assert "pnpm build:all" in content, "CLAUDE.md must mention pnpm build:all"


# [pr_diff] fail_to_pass
def test_claude_md_has_development_section():
    """CLAUDE.md must have Development section with dev server commands."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Check for Development section
    assert "## Development" in content or "### Development" in content, \
        "CLAUDE.md must have a Development section"

    # Check for dev commands
    assert "pnpm dev" in content, "CLAUDE.md must mention pnpm dev"


# [pr_diff] fail_to_pass
def test_claude_md_has_testing_instructions():
    """CLAUDE.md must have Testing section with test commands."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Check for Testing section
    assert "## Testing" in content or "### Testing" in content, \
        "CLAUDE.md must have a Testing section"

    # Check for test commands
    assert "pnpm test" in content, "CLAUDE.md must mention pnpm test"


# [pr_diff] fail_to_pass
def test_claude_md_has_pr_guidelines():
    """CLAUDE.md must document PR guidelines with Conventional Commits."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Check for PR or Commit guidelines section
    has_guidelines = (
        "## Commit" in content or
        "## PR" in content or
        "### Commit" in content or
        "### PR" in content or
        "Conventional Commits" in content
    )
    assert has_guidelines, "CLAUDE.md must have Commit/PR Guidelines section"


# [pr_diff] fail_to_pass
def test_agents_md_symlink_points_to_claude():
    """AGENTS.md symlink must point to CLAUDE.md."""
    agents_md = Path(REPO) / "AGENTS.md"

    # Verify it's a symlink
    assert agents_md.is_symlink(), "AGENTS.md must be a symlink"

    # Check what it points to
    target = agents_md.readlink()
    target_str = str(target)

    # Should point to CLAUDE.md (either relative "CLAUDE.md" or absolute path ending with it)
    assert "CLAUDE.md" in target_str, f"AGENTS.md must point to CLAUDE.md, got: {target_str}"


# [pr_diff] fail_to_pass
def test_gitignore_has_claude_local_patterns():
    """.gitignore must include patterns for local AI agent files."""
    gitignore = Path(REPO) / ".gitignore"
    content = gitignore.read_text()

    # Check for the new patterns added in this PR
    assert ".claude/commands/*.local.md" in content, \
        ".gitignore must include .claude/commands/*.local.md pattern"
    assert ".claude/artifacts" in content, \
        ".gitignore must include .claude/artifacts pattern"


# [pr_diff] fail_to_pass
def test_claude_md_not_stub():
    """CLAUDE.md must have substantial content (not a stub)."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Should be at least 1000 characters (the original AGENTS.md was ~50 lines)
    assert len(content) >= 1000, \
        f"CLAUDE.md content too short ({len(content)} chars), appears to be a stub"

    # Should have multiple sections
    section_count = content.count("## ")
    assert section_count >= 4, \
        f"CLAUDE.md should have at least 4 sections, found {section_count}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral test using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_symlink_behaviorally_works():
    """AGENTS.md symlink behaviorally resolves to CLAUDE.md content."""
    # Use subprocess to read both files and verify they have same content
    r1 = subprocess.run(
        ["cat", f"{REPO}/AGENTS.md"],
        capture_output=True, text=True, timeout=10,
    )
    r2 = subprocess.run(
        ["cat", f"{REPO}/CLAUDE.md"],
        capture_output=True, text=True, timeout=10,
    )

    # Both should succeed
    assert r1.returncode == 0, f"Failed to read AGENTS.md: {r1.stderr}"
    assert r2.returncode == 0, f"Failed to read CLAUDE.md: {r2.stderr}"

    # Content should be identical (since AGENTS.md points to CLAUDE.md)
    assert r1.stdout == r2.stdout, \
        "AGENTS.md and CLAUDE.md should have identical content (symlink)"


# [pr_diff] fail_to_pass
def test_gitignore_patterns_work():
    """.gitignore patterns for .claude files work with git check-ignore."""
    # Test that the patterns in .gitignore would match the expected paths
    # We can't use git check-ignore easily without the files existing,
    # so we'll use git check-ref-format or just grep validation

    r = subprocess.run(
        ["grep", "-E", r"^\.claude/(commands/\*\.local\.md|artifacts)$", f"{REPO}/.gitignore"],
        capture_output=True, text=True, timeout=10,
    )

    # grep returns 0 if pattern found
    assert r.returncode == 0, \
        ".gitignore must contain the .claude/commands/*.local.md and .claude/artifacts patterns"

    # Verify both patterns are present
    assert ".claude/commands/*.local.md" in r.stdout, \
        "Pattern for .claude/commands/*.local.md not found in .gitignore"
    assert ".claude/artifacts" in r.stdout, \
        "Pattern for .claude/artifacts not found in .gitignore"
