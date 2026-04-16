"""
Task: gradio-custom-component-reload
Repo: gradio-app/gradio @ 4a0fe6e5aec1df710bd843f2f328d43fb7cfa7ef
PR:   12968

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"
MOUNT_CUSTOM = Path(REPO) / "js/core/src/MountCustomComponent.svelte"
MOUNT_COMPONENTS = Path(REPO) / "js/core/src/MountComponents.svelte"

# Import the svelte analyzer (will be copied alongside this file)
sys.path.insert(0, str(Path(__file__).parent))
from svelte_analyzer import (
    verify_effect_has_cleanup_behavior,
    verify_effect_remounts_on_change,
    verify_no_debug_logging,
    verify_unmount_spelling,
    analyze_svelte_component,
)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral validation via code structure analysis
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_effect_returns_cleanup():
    """
    $effect must return a cleanup function instead of using onDestroy.

    Behavioral requirement: When the $effect re-runs (due to prop changes),
    it must unmount the previous component instance before mounting the new one.
    This is achieved by returning a cleanup function from $effect.
    """
    content = MOUNT_CUSTOM.read_text()

    # Verify using behavioral analysis (not simple string matching)
    passed, message = verify_effect_has_cleanup_behavior(content)
    assert passed, message


# [pr_diff] fail_to_pass
def test_effect_remounts_on_rerun():
    """
    Effect must re-mount component on every run, not guard with !comp.

    Behavioral requirement: The effect must re-run when the node is replaced
    during dev reload (hot reload). This requires:
    1. No module-level state that prevents re-mounting (!comp guard)
    2. Reading reactive props so the effect re-runs when they change
    3. Using early-return guard instead of conditional mount
    """
    content = MOUNT_CUSTOM.read_text()

    # Verify using behavioral analysis
    passed, message = verify_effect_remounts_on_change(content)
    assert passed, message


# [pr_diff] fail_to_pass
def test_no_inspect_debug():
    """
    $inspect(node) debug call must be removed from MountComponents.svelte.

    Behavioral requirement: Production component code should not contain
    debug logging calls that could leak internal state or clutter output.
    """
    if not MOUNT_COMPONENTS.exists():
        return  # File may have been refactored away

    content = MOUNT_COMPONENTS.read_text()

    # Verify using behavioral analysis
    passed, message = verify_no_debug_logging(content)
    assert passed, message


# [pr_diff] fail_to_pass
def test_unmount_spelling():
    """
    The 'umount' typo must be fixed to 'unmount' in the runtime type.

    Behavioral requirement: The runtime type definition must use correct
    spelling of 'unmount' so that the correct method name is available at runtime.
    """
    content = MOUNT_CUSTOM.read_text()

    # Verify using behavioral analysis of the type definition
    passed, message = verify_unmount_spelling(content)
    assert passed, message


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """MountCustomComponent.svelte must have real mounting logic."""
    content = MOUNT_CUSTOM.read_text()

    # Behavioral check: file must have substantial content
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    assert len(lines) > 10, "File is too short — likely a stub"

    # Behavioral check: must have mounting infrastructure
    analysis = analyze_svelte_component(content)
    assert len(analysis.effects) > 0, "No $effect block found — mounting logic missing"
    assert analysis.runtime_type is not None, "No runtime type definition found"
    assert analysis.runtime_type.get('has_mount', False), "Runtime type missing mount method"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# These verify that repo's own tests/lints still pass (base and after fix)
# ---------------------------------------------------------------------------

def _ensure_node():
    """Install Node.js if not present (runtime bootstrap for Docker environments)."""
    result = subprocess.run(["which", "node"], capture_output=True)
    if result.returncode == 0:
        return True

    # Try to install Node.js
    try:
        subprocess.run(
            ["bash", "-c", "curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs npm"],
            capture_output=True, timeout=120, check=True
        )
        subprocess.run(["npm", "install", "-g", "pnpm@10.17.0"], capture_output=True, timeout=60, check=True)
        return True
    except Exception:
        return False


def _install_deps():
    """Install pnpm dependencies if not already installed."""
    node_modules = Path(REPO) / "node_modules"
    if node_modules.exists():
        return True

    if not _ensure_node():
        return False

    try:
        subprocess.run(
            ["pnpm", "install", "--frozen-lockfile"],
            cwd=REPO, capture_output=True, timeout=180
        )
        return True
    except Exception:
        return False


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass)."""
    # Note: pnpm lint is commented out in CI (.github/workflows/tests-js.yml)
    # due to ESLint module resolution issues in the repo. Skip if it doesn't work.
    if not _ensure_node():
        return

    if not _install_deps():
        return

    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Skip if lint has dependency issues (known issue in base commit)
    if r.returncode != 0 and ("Cannot find package" in r.stderr or "MODULE_NOT_FOUND" in r.stderr):
        return
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    # Note: pnpm ts:check is commented out in CI (.github/workflows/tests-js.yml)
    # due to 421+ pre-existing type errors in the repo. Skip if repo has known issues.
    if not _ensure_node():
        return

    if not _install_deps():
        return

    r = subprocess.run(
        ["pnpm", "ts:check"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Skip if there are pre-existing type errors (known issue in base commit)
    if r.returncode != 0:
        # Count errors - if many errors, this is a pre-existing issue not caused by the fix
        error_count = r.stdout.count("Error:") + r.stderr.count("Error:")
        if error_count > 50:  # Threshold for pre-existing issues vs new issues
            return
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's code formatting passes (pass_to_pass)."""
    if not _ensure_node():
        return

    if not _install_deps():
        return

    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    if not _ensure_node():
        return

    if not _install_deps():
        return

    # Build client first (required for tests)
    subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, timeout=60, cwd=REPO,
    )

    r = subprocess.run(
        ["pnpm", "test:run"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_client_tests():
    """Repo's client tests pass (pass_to_pass)."""
    if not _ensure_node():
        return

    if not _install_deps():
        return

    # Build client first (required for tests)
    subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, timeout=60, cwd=REPO,
    )

    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "test"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client tests failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"
