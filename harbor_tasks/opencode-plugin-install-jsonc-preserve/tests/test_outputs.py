"""
Task: opencode-plugin-install-jsonc-preserve
Repo: anomalyco/opencode @ afb6abff73bdc1577f7388d8273e2eba69849e08
PR:   #19938

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import shutil
from pathlib import Path

REPO = "/workspace/opencode"
INSTALL_TS = f"{REPO}/packages/opencode/src/plugin/install.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """install.ts must parse without syntax errors."""
    r = subprocess.run(
        ["bun", "build", "--no-bundle", "src/plugin/install.ts", "--outfile", "/tmp/gate-check.js"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"install.ts has syntax errors:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_comments_preserved_on_add():
    """Adding a plugin must not strip JSONC comments from config files."""
    src = Path("/tests/test_add_comments.ts")
    dst = Path(f"{REPO}/packages/opencode/test/plugin/test_add_comments.ts")
    try:
        shutil.copy2(src, dst)
        r = subprocess.run(
            ["bun", "run", "test/plugin/test_add_comments.ts"],
            cwd=f"{REPO}/packages/opencode",
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, (
            f"JSONC comments stripped on add:\n{r.stdout.decode()}\n{r.stderr.decode()}"
        )
    finally:
        dst.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_comments_preserved_on_force_replace():
    """Force-replacing a plugin must not strip JSONC comments."""
    src = Path("/tests/test_force_comments.ts")
    dst = Path(f"{REPO}/packages/opencode/test/plugin/test_force_comments.ts")
    try:
        shutil.copy2(src, dst)
        r = subprocess.run(
            ["bun", "run", "test/plugin/test_force_comments.ts"],
            cwd=f"{REPO}/packages/opencode",
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, (
            f"JSONC comments stripped on force replace:\n{r.stdout.decode()}\n{r.stderr.decode()}"
        )
    finally:
        dst.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Upstream plugin install test suite still passes."""
    # Clean up any leftover behavioral test files
    for f in ["test_add_comments.ts", "test_force_comments.ts"]:
        Path(f"{REPO}/packages/opencode/test/plugin/{f}").unlink(missing_ok=True)

    r = subprocess.run(
        ["bun", "test", "test/plugin/install.test.ts"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"Existing tests regressed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ afb6abff
def test_no_any_type():
    """install.ts must not use the `any` type (AGENTS.md: 'Avoid using the any type')."""
    content = Path(INSTALL_TS).read_text()
    lines = content.splitlines()
    violations = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        # Skip comments
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
            continue
        # Check for `: any`, `<any>`, `as any`

        if re.search(r':\s*any\b|<any>|\bas\s+any\b', line):
            violations.append(f"  line {i}: {line.strip()}")
    assert not violations, "Found `any` type usage in install.ts:\n" + "\n".join(violations)


# [agent_config] pass_to_pass — AGENTS.md:84 @ afb6abff
def test_no_else_statements():
    """install.ts must not use else statements (AGENTS.md: 'Avoid else. Prefer early returns.')."""
    content = Path(INSTALL_TS).read_text()
    lines = content.splitlines()
    violations = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue

        if re.search(r'\}\s*else\b', line):
            violations.append(f"  line {i}: {line.strip()}")
    assert not violations, "Found else statements in install.ts:\n" + "\n".join(violations)


# [agent_config] pass_to_pass — AGENTS.md:12 @ afb6abff
def test_no_try_catch():
    """install.ts must not use try/catch blocks (AGENTS.md: 'Avoid try/catch where possible')."""
    content = Path(INSTALL_TS).read_text()
    lines = content.splitlines()
    violations = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
            continue

        if re.search(r'\btry\s*\{', line) or re.search(r'\}\s*catch\b', line):
            violations.append(f"  line {i}: {line.strip()}")
    assert not violations, "Found try/catch in install.ts:\n" + "\n".join(violations)
