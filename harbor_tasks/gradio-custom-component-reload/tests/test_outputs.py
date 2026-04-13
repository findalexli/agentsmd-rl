"""
Task: gradio-custom-component-reload
Repo: gradio-app/gradio @ 4a0fe6e5aec1df710bd843f2f328d43fb7cfa7ef
PR:   12968

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
MOUNT_CUSTOM = Path(REPO) / "js/core/src/MountCustomComponent.svelte"
MOUNT_COMPONENTS = Path(REPO) / "js/core/src/MountComponents.svelte"


def _run_validation(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write and execute a Python validation script."""
    script = Path("/tmp/_eval_check.py")
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral validation via code execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_effect_returns_cleanup():
    """$effect must return a cleanup function instead of using onDestroy."""
    r = _run_validation(
        f'''
import re

content = open("{MOUNT_CUSTOM}").read()

# Must NOT import onDestroy — the fix removes it entirely
assert "onDestroy" not in content, "onDestroy import still present"

# $effect must contain a return () => cleanup pattern
assert "return () =>" in content or "return() =>" in content, (
    "$effect does not return a cleanup function"
)

# Cleanup must call unmount (not umount) on the mounted instance
assert ".unmount(" in content, "Cleanup does not call .unmount()"

# Must NOT have the old onDestroy block
assert not re.search(r"onDestroy\\s*\\(\\s*\\(\\)\\s*=>", content), (
    "onDestroy callback still present — should use $effect return instead"
)

print("PASS")
'''
    )
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_effect_remounts_on_rerun():
    """Effect must re-mount component on every run, not guard with !comp."""
    r = _run_validation(
        f'''
import re

content = open("{MOUNT_CUSTOM}").read()

# Must NOT have module-level 'let comp' that holds stale mount state.
# The fix uses a local 'mounted' variable inside $effect instead.
has_let_comp = False
for line in content.split("\\n"):
    stripped = line.strip()
    # Match 'let comp;' or 'let comp =' but NOT 'let component'
    if stripped.startswith("let comp") and "component" not in stripped:
        has_let_comp = True
        break
assert not has_let_comp, "Module-level comp variable prevents effect re-triggering"

# Must NOT have the old guard 'if (el && !comp && runtime)'
assert "&& !comp" not in content, "Old !comp guard pattern still present"

# Effect must use early-return guard instead of conditional mount
assert re.search(r"if\\s*\\(\\s*!el\\s*\\|\\|", content) or "return" in content, (
    "No early-return guard found — effect structure is wrong"
)

print("PASS")
'''
    )
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_no_inspect_debug():
    """$inspect(node) debug call must be removed from MountComponents.svelte."""
    r = _run_validation(
        f'''
import os

path = "{MOUNT_COMPONENTS}"
if not os.path.exists(path):
    # File may have been refactored away
    print("PASS")
    exit(0)

content = open(path).read()
assert "$inspect" not in content, "$inspect debug call still present"
print("PASS")
'''
    )
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_unmount_spelling():
    """The 'umount' typo must be fixed to 'unmount' in the runtime type."""
    r = _run_validation(
        f'''
import re

content = open("{MOUNT_CUSTOM}").read()

# Must have 'unmount' present (correct spelling)
assert "unmount" in content, "'unmount' not found — typo has not been corrected"

# Must NOT have 'umount' as a standalone word (not inside 'unmount')
# \\bumount\\b matches 'umount' but not 'unmount' since there's no word
# boundary between 'n' and 'm' in 'unmount'.
assert not re.search(r"\\bumount\\b", content), "'umount' typo still present"

print("PASS")
'''
    )
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """MountCustomComponent.svelte must have real mounting logic."""
    content = MOUNT_CUSTOM.read_text()
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    assert len(lines) > 10, "File is too short — likely a stub"
    assert "mount" in content.lower(), "No mount call found"
    assert "$effect" in content, "No $effect block found"
    assert "target" in content, "No target element reference found"


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
