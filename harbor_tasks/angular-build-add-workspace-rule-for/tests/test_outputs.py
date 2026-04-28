"""
Task: angular-build-add-workspace-rule-for
Repo: angular/angular @ ba009b603119299a03f9d844f93882d42d47d150
PR:   67018

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import pytest
from pathlib import Path

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

def test_agent_rules_content_matches():
    """.agent/rules/agents.md exists and has same content as AGENTS.md.

    Behavior: Reading from .agent/rules/agents.md yields identical content to AGENTS.md.
    This verifies the workspace rule is accessible regardless of implementation
    (symlink, copy, hardlink, or bind mount).
    """
    agents_path = Path(f"{REPO}/AGENTS.md")
    rules_path = Path(f"{REPO}/.agent/rules/agents.md")

    assert agents_path.exists(), "AGENTS.md does not exist"
    assert rules_path.exists(), ".agent/rules/agents.md does not exist"

    agents_content = agents_path.read_text()
    rules_content = rules_path.read_text()
    assert agents_content == rules_content, \
        f"Content mismatch: {len(rules_content)} chars vs {len(agents_content)} chars"


def test_agents_md_frontmatter_parses():
    """AGENTS.md has valid YAML frontmatter with trigger: always_on.

    Behavior: Parses as valid YAML with specific key-value pair.
    """
    import re
    import yaml

    content = Path(f"{REPO}/AGENTS.md").read_text()

    m = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    assert m, "No YAML frontmatter found in AGENTS.md"

    try:
        frontmatter = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML frontmatter: {e}")

    assert isinstance(frontmatter, dict), f"Frontmatter must be a dict, got {type(frontmatter)}"
    assert 'trigger' in frontmatter, f"Frontmatter missing 'trigger' key"
    assert frontmatter['trigger'] == 'always_on', \
        f"trigger must be 'always_on', got: {frontmatter['trigger']}"


def test_prettierignore_excludes_agent_rules():
    """.prettierignore excludes .agent/rules/agents.md.

    Behavior: Running prettier --check on .agent/rules/agents.md verifies
    the file is ignored (prettier skips it).
    """
    ignore_file = Path(f"{REPO}/.prettierignore")
    assert ignore_file.exists(), ".prettierignore does not exist"

    # Verify the entry exists in .prettierignore
    content = ignore_file.read_text()
    assert '.agent/rules/agents.md' in content, \
        ".prettierignore missing .agent/rules/agents.md entry"

    # Behavioral: confirm prettier does not format the file.
    # Prettier may either ignore it (via .prettierignore) or refuse to
    # process it because it is a symlink — both are correct behavior.
    r = subprocess.run(
        ["npx", "prettier", "--check", ".agent/rules/agents.md"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    ok = (r.returncode == 0
          or (r.returncode == 2 and "symbolic link" in r.stderr))
    assert ok, \
        f"Prettier should skip .agent/rules/agents.md (rc={r.returncode}): {r.stderr[:300]}"


def test_pullapprove_covers_agent_directory():
    """.pullapprove.yml includes .agent/**/{*,.*} glob pattern.

    Behavior: The pullapprove configuration covers files in .agent/rules/.
    """
    pullapprove_file = Path(f"{REPO}/.pullapprove.yml")
    assert pullapprove_file.exists(), ".pullapprove.yml does not exist"

    # Verify the glob pattern is present in the configuration
    content = pullapprove_file.read_text()
    assert '.agent/**/{*,.*}' in content, \
        ".pullapprove.yml missing .agent/**/{*,.*} glob pattern"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

def test_agents_md_has_environment_section():
    """AGENTS.md retains core environment documentation."""
    content = Path(f"{REPO}/AGENTS.md").read_text()
    assert "## Environment" in content, "Missing ## Environment section"
    assert "pnpm" in content, "Missing pnpm reference"


def test_prettierignore_exists():
    """.prettierignore file exists and has content."""
    p = Path(f"{REPO}/.prettierignore")
    assert p.exists(), ".prettierignore missing"
    assert len(p.read_text().strip()) > 0, ".prettierignore is empty"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# ---------------------------------------------------------------------------

def test_repo_tslint(install_deps):
    """Repo's TSLint passes."""
    r = subprocess.run(
        ["pnpm", "tslint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"TSLint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_check_tooling_setup(install_deps):
    """Repo's TypeScript tooling setup compiles."""
    r = subprocess.run(
        ["pnpm", "check-tooling-setup"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Tooling setup check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_pullapprove_verify(install_deps):
    """Repo's PullApprove config is valid."""
    r = subprocess.run(
        ["pnpm", "ng-dev", "pullapprove", "verify"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"PullApprove verify failed:\n{r.stderr[-500:]}"


def test_repo_ngbot_verify(install_deps):
    """Repo's NgBot config is valid."""
    r = subprocess.run(
        ["pnpm", "ng-dev", "ngbot", "verify"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"NgBot verify failed:\n{r.stderr[-500:]}"
