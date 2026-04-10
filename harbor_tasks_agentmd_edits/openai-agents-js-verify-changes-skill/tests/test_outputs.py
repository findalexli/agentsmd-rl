"""
Task: openai-agents-js-verify-changes-skill
Repo: openai/openai-agents-js @ b54fc4a3222ea8b14b1c3a8e45457b4905354bee
PR:   826

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/openai-agents-js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Shell scripts must have valid bash syntax."""
    run_sh = Path(REPO) / ".codex/skills/verify-changes/scripts/run.sh"
    assert run_sh.exists(), "run.sh must exist"
    r = subprocess.run(
        ["bash", "-n", str(run_sh)],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, f"run.sh has syntax errors:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm lint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's TypeScript build passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build_check():
    """Repo's build-check (typecheck examples) passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm build && pnpm -r build-check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build-check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm build && pnpm test -- --run"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for the skill scripts
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_run_sh_exists_with_verification_commands():
    """run.sh must exist and contain the full pnpm verification sequence."""
    run_sh = Path(REPO) / ".codex/skills/verify-changes/scripts/run.sh"
    assert run_sh.exists(), ".codex/skills/verify-changes/scripts/run.sh must exist"
    content = run_sh.read_text()
    assert "pnpm i" in content or "pnpm install" in content, \
        "run.sh should install dependencies"
    assert "pnpm build" in content, "run.sh should run build"
    assert "pnpm lint" in content, "run.sh should run lint"
    assert "pnpm test" in content, "run.sh should run tests"
    assert "build-check" in content, "run.sh should run build-check"


# [pr_diff] fail_to_pass
def test_run_sh_fail_fast():
    """run.sh must use fail-fast semantics (set -e or equivalent)."""
    run_sh = Path(REPO) / ".codex/skills/verify-changes/scripts/run.sh"
    assert run_sh.exists(), "run.sh must exist"
    content = run_sh.read_text()
    assert "set -e" in content or "set -euo" in content, \
        "run.sh should use set -e for fail-fast semantics"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit (config_edit) — AGENTS.md must reference the new skill
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — AGENTS.md retains existing structure
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [config_edit] fail_to_pass
