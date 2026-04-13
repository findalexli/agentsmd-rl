"""
Task: remix-add-supersede-pr-skill-ts-helper
Repo: remix-run/remix @ 64b3a160dc25bbb082b96673e12bb55935f3528d
PR:   11088

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"


def _run_ts(script_path: str, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a TypeScript file with Node's native TS strip-types support."""
    return subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings", script_path] + args,
        capture_output=True, text=True, timeout=timeout,
        cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """TypeScript script parses without errors."""
    script = Path(REPO) / "skills" / "supersede-pr" / "scripts" / "close_superseded_pr.ts"
    assert script.exists(), f"Script not found: {script}"
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings", "--check", str(script)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript syntax check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_script_help_flag():
    """close_superseded_pr.ts --help prints usage and exits 0."""
    script = str(Path(REPO) / "skills" / "supersede-pr" / "scripts" / "close_superseded_pr.ts")
    r = _run_ts(script, ["--help"])
    assert r.returncode == 0, f"--help exited with {r.returncode}: {r.stderr}"
    assert "Usage" in r.stdout, f"Expected 'Usage' in help output, got: {r.stdout}"
    assert "old_pr" in r.stdout, f"Help should mention old_pr argument"
    assert "--dry-run" in r.stdout, f"Help should mention --dry-run flag"


# [pr_diff] fail_to_pass
def test_script_rejects_same_pr():
    """Script rejects when old_pr == new_pr."""
    script = str(Path(REPO) / "skills" / "supersede-pr" / "scripts" / "close_superseded_pr.ts")
    r = _run_ts(script, ["42", "42", "--repo", "remix-run/remix"])
    assert r.returncode != 0, "Should fail when old_pr == new_pr"
    assert "must be different" in r.stderr, f"Expected 'must be different' in stderr: {r.stderr}"


# [pr_diff] fail_to_pass
def test_script_rejects_non_numeric():
    """Script rejects non-numeric PR numbers."""
    script = str(Path(REPO) / "skills" / "supersede-pr" / "scripts" / "close_superseded_pr.ts")
    for bad_input, label in [("abc", "old_pr"), ("12x", "old_pr")]:
        r = _run_ts(script, [bad_input, "100"])
        assert r.returncode != 0, f"Should fail for non-numeric {label}: {bad_input}"
        assert "numeric" in r.stderr.lower(), \
            f"Expected 'numeric' in stderr for input '{bad_input}': {r.stderr}"


# [pr_diff] fail_to_pass
def test_supersede_pr_skill_md():
    """supersede-pr SKILL.md exists with correct frontmatter and content."""
    skill = Path(REPO) / "skills" / "supersede-pr" / "SKILL.md"
    assert skill.exists(), f"SKILL.md not found: {skill}"
    content = skill.read_text()
    assert "name: supersede-pr" in content, "SKILL.md should have name: supersede-pr in frontmatter"
    assert "Closes #" in content or "closing keywords" in content.lower(), \
        "SKILL.md should explain why GitHub closing keywords don't work for PRs"
    assert "gh pr close" in content or "close_superseded_pr" in content, \
        "SKILL.md should reference the close command or script"


# [pr_diff] fail_to_pass
def test_make_pr_skill_md():
    """make-pr SKILL.md exists with correct frontmatter and content."""
    skill = Path(REPO) / "skills" / "make-pr" / "SKILL.md"
    assert skill.exists(), f"SKILL.md not found: {skill}"
    content = skill.read_text()
    assert "name: make-pr" in content, "SKILL.md should have name: make-pr in frontmatter"
    assert "gh pr create" in content, "SKILL.md should reference gh pr create"


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_scripts_rule():
    """AGENTS.md must document one-off scripts as TypeScript convention."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    content_lower = content.lower()
    assert "one-off scripts" in content_lower or "one-off" in content_lower, \
        "AGENTS.md should have a one-off scripts coding convention"
    assert "typescript" in content_lower, \
        "The one-off scripts rule should mention TypeScript"
    assert "node" in content_lower, \
        "The one-off scripts rule should mention Node.js"


# [pr_diff] fail_to_pass
def test_agents_md_skills_section():
    """AGENTS.md must have a Skills section listing both skills."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    assert "## Skills" in content or "## skills" in content.lower(), \
        "AGENTS.md should have a Skills heading"
    assert "supersede-pr" in content, \
        "Skills section should list supersede-pr"
    assert "make-pr" in content, \
        "Skills section should list make-pr"
    assert "SKILL.md" in content, \
        "Skills section should reference SKILL.md files"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — existing rules preserved
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:26 @ 64b3a160dc25bbb082b96673e12bb55935f3528d
def test_agents_md_preserves_let_rule():
    """AGENTS.md must still have the let/const variable convention."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    assert "let" in content and "const" in content, \
        "AGENTS.md should still have let/const variable convention"
    assert "var" in content.lower(), \
        "AGENTS.md should still reference var (to say never use it)"


# [agent_config] pass_to_pass — AGENTS.md:25 @ 64b3a160dc25bbb082b96673e12bb55935f3528d
def test_script_uses_let_not_var():
    """The TS script follows AGENTS.md let/const convention (no var)."""
    script = Path(REPO) / "skills" / "supersede-pr" / "scripts" / "close_superseded_pr.ts"
    if not script.exists():
        return  # Script not created yet; other f2p tests will catch this
    content = script.read_text()
    # Check no var declarations (but allow 'var' inside strings/comments)
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//"):
            continue
        assert not stripped.startswith("var "), \
            f"Line {i} uses 'var' instead of 'let/const' per AGENTS.md: {line.strip()}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass (repo_tests) — ensure repo's own checks pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — .github/workflows/check.yaml
def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — .github/workflows/check.yaml
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — .github/workflows/format.yml (check only)
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — .github/workflows/check.yaml
def test_repo_changes_validate():
    """Repo's change files validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "changes:validate"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Changes validate failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — .github/workflows/build.yaml
def test_repo_build():
    """Repo's build passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
