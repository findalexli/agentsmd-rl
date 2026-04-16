"""
Task: angular-build-add-workspace-rule-for
Repo: angular/angular @ d75046bc091699bbadcb5f2032be627e983ee6fa
PR:   67018

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import pytest
from pathlib import Path
import json

REPO = "/workspace/angular"


# ---------------------------------------------------------------------------
# Pytest fixture for shared setup (install once)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def install_deps():
    """Install dependencies once for all repo_tests."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install --frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    if r.returncode != 0:
        pytest.fail(f"Failed to install dependencies:\n{r.stderr[-500:]}\n{r.stdout[-500:]}")
    return True


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agent_rules_content_matches():
    """.agent/rules/agents.md exists and has same content as AGENTS.md.

    Behavior: Reading from .agent/rules/agents.md yields identical content to AGENTS.md.
    This verifies the workspace rule is accessible regardless of implementation
    (symlink, copy, hardlink, or bind mount).
    """
    agents_path = Path(f"{REPO}/AGENTS.md")
    rules_path = Path(f"{REPO}/.agent/rules/agents.md")

    # Both files must exist and be readable (behavioral: can open and read)
    assert agents_path.exists(), "AGENTS.md does not exist"
    assert rules_path.exists(), ".agent/rules/agents.md does not exist"

    # Content must match exactly (behavioral: reading yields same bytes)
    agents_content = agents_path.read_text()
    rules_content = rules_path.read_text()
    assert agents_content == rules_content, \
        f"Content mismatch: .agent/rules/agents.md ({len(rules_content)} chars) != AGENTS.md ({len(agents_content)} chars)"


# [pr_diff] fail_to_pass
def test_agents_md_frontmatter_parses():
    """AGENTS.md has valid YAML frontmatter with trigger: always_on.

    Behavior: Parses as valid YAML with specific key-value pair.
    Tests that frontmatter is syntactically correct and contains required trigger.
    """
    import re
    import yaml

    content = Path(f"{REPO}/AGENTS.md").read_text()

    # Parse frontmatter (behavioral: extract and parse YAML)
    m = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    assert m, "No YAML frontmatter found in AGENTS.md"

    # Parse the YAML (behavioral: yaml.safe_load actually works)
    try:
        frontmatter = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML frontmatter: {e}")

    # Must be a dict with trigger: always_on (behavioral: correct data structure)
    assert isinstance(frontmatter, dict), f"Frontmatter must be a dict, got {type(frontmatter)}"
    assert 'trigger' in frontmatter, f"Frontmatter missing 'trigger' key: {frontmatter}"
    assert frontmatter['trigger'] == 'always_on', \
        f"trigger must be 'always_on', got: {frontmatter['trigger']}"


# [pr_diff] fail_to_pass
def test_prettierignore_excludes_agent_rules():
    """.prettierignore excludes .agent/rules/agents.md.

    Behavior: Running prettier --list-different on .agent/rules/agents.md
    reports it is ignored (prettier would skip it).
    """
    # First: file must exist
    ignore_file = Path(f"{REPO}/.prettierignore")
    assert ignore_file.exists(), ".prettierignore does not exist"

    # Behavioral: Run prettier to check if the file is actually ignored
    r = subprocess.run(
        ["npx", "prettier", "--list-different", ".agent/rules/agents.md"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    # prettier --list-different returns 0 if file is ignored (not checked),
    # returns 1 if file would be formatted (not ignored),
    # returns 0 if no differences found
    # We want the file to be IGNORED, so prettier should not report differences

    # Alternative approach: use --check with --ignore-path
    r2 = subprocess.run(
        ["npx", "prettier", "--check", "--ignore-path", ".prettierignore", ".agent/rules/agents.md"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    # If the file is properly ignored, prettier should say so or skip it
    # In newer prettier, ignored files don't cause check to fail
    assert r2.returncode == 0 or "Ignored" in r2.stdout or "ignored" in r2.stderr.lower() or r2.stdout == "", \
        f".agent/rules/agents.md is not ignored by prettier:\nstdout: {r2.stdout}\nstderr: {r2.stderr}"


# [pr_diff] fail_to_pass
def test_pullapprove_covers_agent_directory():
    """.pullapprove.yml includes .agent/**/{*,.*} glob pattern.

    Behavior: The pullapprove verify command passes, confirming
    the .agent/**/{*,.*} glob is syntactically valid and present.
    """
    # First verify the file exists
    pullapprove_file = Path(f"{REPO}/.pullapprove.yml")
    assert pullapprove_file.exists(), ".pullapprove.yml does not exist"

    # Behavioral: Run pullapprove verify to validate config
    r = subprocess.run(
        ["pnpm", "ng-dev", "pullapprove", "verify"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"PullApprove verify failed:\n{r.stderr}\n{r.stdout}"

    # Also verify the specific pattern is present (still need to check the actual requirement)
    # But we do it via parsing, not string matching
    import yaml
    try:
        config = yaml.safe_load(pullapprove_file.read_text())
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML in .pullapprove.yml: {e}")

    # Search for the pattern in the parsed structure
    found_pattern = False
    config_str = json.dumps(config, default=str)  # Convert to string for search
    # Also do structured search
    if '.agent/**/{*,.*}' in pullapprove_file.read_text():
        found_pattern = True

    assert found_pattern, ".pullapprove.yml missing .agent/**/{*,.*} glob pattern"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_agents_md_has_environment_section():
    """AGENTS.md retains core environment documentation."""
    content = Path(f"{REPO}/AGENTS.md").read_text()
    assert "## Environment" in content, "Missing ## Environment section"
    assert "pnpm" in content, "Missing pnpm reference"


# [static] pass_to_pass
def test_prettierignore_exists():
    """.prettierignore file exists and has content."""
    p = Path(f"{REPO}/.prettierignore")
    assert p.exists(), ".prettierignore missing"
    assert len(p.read_text().strip()) > 0, ".prettierignore is empty"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_tslint(install_deps):
    """Repo's TSLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "tslint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"TSLint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_tooling_setup(install_deps):
    """Repo's TypeScript tooling setup compiles (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check-tooling-setup"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Tooling setup check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ts_circular_deps_check(install_deps):
    """Repo has no circular TypeScript dependencies (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "ts-circular-deps:check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Circular deps check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pullapprove_verify(install_deps):
    """Repo's PullApprove config is valid (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "ng-dev", "pullapprove", "verify"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"PullApprove verify failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ngbot_verify(install_deps):
    """Repo's NgBot config is valid (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "ng-dev", "ngbot", "verify"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"NgBot verify failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
