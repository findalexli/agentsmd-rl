"""
Task: openai-agents-js-parallel-verification
Repo: openai/openai-agents-js @ 05dd513231c04ffb6013a25118605a7a72a9a063
PR:   1120

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/openai-agents-js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_run_mjs_syntax_valid():
    """run.mjs must parse without JavaScript syntax errors."""
    mjs = Path(REPO) / ".agents/skills/code-change-verification/scripts/run.mjs"
    assert mjs.exists(), "run.mjs does not exist"
    r = subprocess.run(
        ["node", "--check", str(mjs)],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"run.mjs has syntax errors:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_run_mjs_exists():
    """The new Node runner script run.mjs must exist."""
    mjs = Path(REPO) / ".agents/skills/code-change-verification/scripts/run.mjs"
    assert mjs.exists(), (
        "Expected .agents/skills/code-change-verification/scripts/run.mjs to exist"
    )
    content = mjs.read_text()
    assert len(content) > 100, "run.mjs appears to be empty or trivially small"


# [pr_diff] fail_to_pass
def test_run_mjs_exports_create_default_plan():
    """run.mjs must export a createDefaultPlan function that returns sequential and parallel steps."""
    mjs = Path(REPO) / ".agents/skills/code-change-verification/scripts/run.mjs"
    assert mjs.exists(), "run.mjs does not exist"
    # Execute a small Node script that imports createDefaultPlan and prints the plan
    check_script = f"""
    import {{ createDefaultPlan }} from '{mjs}';
    const plan = createDefaultPlan();
    console.log(JSON.stringify({{
        hasSequential: Array.isArray(plan.sequentialSteps),
        hasParallel: Array.isArray(plan.parallelSteps),
        seqCount: plan.sequentialSteps.length,
        parCount: plan.parallelSteps.length,
    }}));
    """
    r = subprocess.run(
        ["node", "--input-type=module", "-e", check_script],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Failed to import createDefaultPlan:\n{r.stderr.decode()}"
    )
    data = json.loads(r.stdout.decode().strip())
    assert data["hasSequential"], "Plan must have sequentialSteps array"
    assert data["hasParallel"], "Plan must have parallelSteps array"
    assert data["seqCount"] >= 2, "Plan must have at least 2 sequential steps (install, build)"
    assert data["parCount"] >= 2, "Plan must have at least 2 parallel steps"


# [pr_diff] fail_to_pass
def test_run_mjs_sequential_barriers():
    """Install and build must be sequential barrier steps in the plan."""
    mjs = Path(REPO) / ".agents/skills/code-change-verification/scripts/run.mjs"
    assert mjs.exists(), "run.mjs does not exist"
    check_script = f"""
    import {{ createDefaultPlan }} from '{mjs}';
    const plan = createDefaultPlan();
    const labels = plan.sequentialSteps.map(s => s.label);
    console.log(JSON.stringify(labels));
    """
    r = subprocess.run(
        ["node", "--input-type=module", "-e", check_script],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed to get plan:\n{r.stderr.decode()}"
    labels = json.loads(r.stdout.decode().strip())
    assert "install" in labels, f"Sequential steps must include 'install', got {labels}"
    assert "build" in labels, f"Sequential steps must include 'build', got {labels}"


# [pr_diff] fail_to_pass
def test_run_mjs_parallel_validation_steps():
    """Build-check, dist-check, lint, and test must be parallel steps."""
    mjs = Path(REPO) / ".agents/skills/code-change-verification/scripts/run.mjs"
    assert mjs.exists(), "run.mjs does not exist"
    check_script = f"""
    import {{ createDefaultPlan }} from '{mjs}';
    const plan = createDefaultPlan();
    const labels = plan.parallelSteps.map(s => s.label);
    console.log(JSON.stringify(labels));
    """
    r = subprocess.run(
        ["node", "--input-type=module", "-e", check_script],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed to get plan:\n{r.stderr.decode()}"
    labels = json.loads(r.stdout.decode().strip())
    assert "lint" in labels, f"Parallel steps must include 'lint', got {labels}"
    assert "test" in labels, f"Parallel steps must include 'test', got {labels}"
    has_build_check = any("build" in l and "check" in l for l in labels)
    assert has_build_check, f"Parallel steps must include a build-check step, got {labels}"


# [pr_diff] fail_to_pass
def test_run_sh_delegates_to_mjs():
    """run.sh must delegate to run.mjs instead of running pnpm steps directly."""
    run_sh = Path(REPO) / ".agents/skills/code-change-verification/scripts/run.sh"
    assert run_sh.exists(), "run.sh does not exist"
    content = run_sh.read_text()
    assert "run.mjs" in content, "run.sh must reference run.mjs"
    # Should NOT contain the old inline pnpm steps
    assert "pnpm i" not in content, (
        "run.sh should delegate to run.mjs, not run pnpm steps directly"
    )
    assert "pnpm build" not in content, (
        "run.sh should delegate to run.mjs, not run pnpm steps directly"
    )


# [pr_diff] fail_to_pass
def test_run_ps1_delegates_to_mjs():
    """run.ps1 must delegate to run.mjs instead of running pnpm steps directly."""
    run_ps1 = Path(REPO) / ".agents/skills/code-change-verification/scripts/run.ps1"
    assert run_ps1.exists(), "run.ps1 does not exist"
    content = run_ps1.read_text()
    assert "run.mjs" in content, "run.ps1 must reference run.mjs"
    # Should NOT contain the old Invoke-PnpmStep function
    assert "Invoke-PnpmStep" not in content, (
        "run.ps1 should delegate to run.mjs, not define Invoke-PnpmStep"
    )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_run_mjs_has_fail_fast():
    """run.mjs must implement fail-fast cancellation for parallel steps."""
    mjs = Path(REPO) / ".agents/skills/code-change-verification/scripts/run.mjs"
    assert mjs.exists(), "run.mjs does not exist"
    content = mjs.read_text()
    # Must have process spawning and signal handling
    assert "spawn" in content, "run.mjs must use spawn for running child processes"
    assert "SIGTERM" in content or "SIGINT" in content, (
        "run.mjs must handle termination signals for fail-fast"
    )
    assert "Promise.race" in content or "Promise.allSettled" in content, (
        "run.mjs must use Promise.race or Promise.allSettled for parallel execution"
    )
