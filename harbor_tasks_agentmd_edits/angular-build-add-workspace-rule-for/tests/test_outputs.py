"""
Task: angular-build-add-workspace-rule-for
Repo: angular/angular @ d75046bc091699bbadcb5f2032be627e983ee6fa
PR:   67018

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/angular"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_symlink_exists_and_resolves():
    """The .agent/rules/agents.md symlink exists and resolves to AGENTS.md content."""
    r = subprocess.run(
        ["python3", "-c", """
import os, sys
symlink = '.agent/rules/agents.md'
if not os.path.exists(symlink):
    print(f"FAIL: {symlink} does not exist")
    sys.exit(1)
if not os.path.islink(symlink):
    print(f"FAIL: {symlink} exists but is not a symlink")
    sys.exit(1)
with open(symlink) as f1, open('AGENTS.md') as f2:
    if f1.read() != f2.read():
        print("FAIL: symlink content doesn't match AGENTS.md")
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_agents_md_has_frontmatter():
    """AGENTS.md has YAML frontmatter with trigger: always_on."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys
content = open('AGENTS.md').read()
m = re.match(r'^---\\n(.*?)\\n---\\n', content, re.DOTALL)
if not m:
    print("FAIL: no YAML frontmatter found")
    sys.exit(1)
if 'trigger:' not in m.group(1) or 'always_on' not in m.group(1):
    print("FAIL: frontmatter missing trigger: always_on")
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_prettierignore_has_agent_entry():
    """.prettierignore includes .agent/rules/agents.md entry."""
    content = Path(f"{REPO}/.prettierignore").read_text()
    assert ".agent/rules/agents.md" in content, \
        ".prettierignore missing .agent/rules/agents.md entry"


# [pr_diff] fail_to_pass
def test_pullapprove_has_agent_glob():
    """.pullapprove.yml includes .agent/**/{*,.*} glob pattern."""
    content = Path(f"{REPO}/.pullapprove.yml").read_text()
    assert ".agent/**/{*,.*}" in content, \
        ".pullapprove.yml missing .agent/**/{*,.*} glob"


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
def test_repo_tslint():
    """Repo's TSLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/angular && corepack enable && pnpm install --frozen-lockfile && pnpm tslint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"TSLint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_tooling_setup():
    """Repo's TypeScript tooling setup compiles (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/angular && corepack enable && pnpm install --frozen-lockfile && pnpm check-tooling-setup"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Tooling setup check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ts_circular_deps_check():
    """Repo has no circular TypeScript dependencies (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/angular && corepack enable && pnpm install --frozen-lockfile && pnpm ts-circular-deps:check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Circular deps check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pullapprove_verify():
    """Repo's PullApprove config is valid (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/angular && corepack enable && pnpm install --frozen-lockfile && pnpm ng-dev pullapprove verify"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"PullApprove verify failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ngbot_verify():
    """Repo's NgBot config is valid (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/angular && corepack enable && pnpm install --frozen-lockfile && pnpm ng-dev ngbot verify"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"NgBot verify failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_config():
    """Repo's config files are properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/angular && corepack enable && pnpm install --frozen-lockfile && pnpm prettier --check package.json pnpm-workspace.yaml renovate.json .github/workflows/ci.yml .github/workflows/pr.yml .pullapprove.yml"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier config check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_buildifier():
    """Repo's Bazel files are properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/angular && corepack enable && pnpm install --frozen-lockfile && ./node_modules/.bin/buildifier -mode=check MODULE.bazel BUILD.bazel REPO.bazel packages.bzl"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Buildifier check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
