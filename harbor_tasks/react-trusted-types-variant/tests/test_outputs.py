"""
Task: react-trusted-types-variant
Repo: facebook/react @ c0c37063e2cd8976d839998573012d48d303ada0

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/shared/forks/ReactFeatureFlags.www-dynamic.js"


def _read_target() -> str:
    return Path(TARGET).read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must be valid JavaScript (no syntax errors)."""
    r = subprocess.run(
        ["node", "--check", TARGET],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Syntax error in {TARGET}:\n{r.stderr.decode()}"
    )


# [static] pass_to_pass
def test_flag_exists_in_file():
    """enableTrustedTypesIntegration must still be declared in the file."""
    content = _read_target()
    assert "enableTrustedTypesIntegration" in content, (
        "Flag 'enableTrustedTypesIntegration' not found in target file"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flag_uses_variant():
    """enableTrustedTypesIntegration must be assigned __VARIANT__, not false."""
    content = _read_target()
    assert "export const enableTrustedTypesIntegration: boolean = __VARIANT__;" in content, (
        "Flag 'enableTrustedTypesIntegration' is not set to __VARIANT__. "
        "Expected: export const enableTrustedTypesIntegration: boolean = __VARIANT__;"
    )


# [pr_diff] fail_to_pass
def test_flag_not_hardcoded_false():
    """enableTrustedTypesIntegration must not be hardcoded to false."""
    content = _read_target()
    assert "enableTrustedTypesIntegration: boolean = false" not in content, (
        "Flag 'enableTrustedTypesIntegration' is still hardcoded to false. "
        "Move it to the __VARIANT__ section."
    )


# [pr_diff] fail_to_pass
def test_flag_not_in_hardcoded_section():
    """Flag must not appear in the TODO/hardcoded section of the file."""
    content = _read_target()
    # Find the TODO section and ensure the flag is not there
    todo_marker = "TODO: These flags are hard-coded"
    assert todo_marker in content, (
        "TODO marker not found in file — file structure may be broken"
    )
    todo_idx = content.index(todo_marker)
    after_todo = content[todo_idx:]
    assert "enableTrustedTypesIntegration" not in after_todo, (
        "Flag 'enableTrustedTypesIntegration' is still present in the hardcoded TODO section. "
        "It must be moved above to the __VARIANT__ section."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_variant_flags_intact():
    """Other __VARIANT__ flags must still be declared correctly (anti-regression)."""
    content = _read_target()
    required_flags = [
        "alwaysThrottleRetries",
        "disableLegacyContextForFunctionComponents",
        "disableSchedulerTimeoutInWorkLoop",
        "enableHiddenSubtreeInsertionEffectCleanup",
        "enableNoCloningMemoCache",
        "enableObjectFiber",
        "enableRetryLaneExpiration",
        "enableTransitionTracing",
        "enableSchedulingProfiler",
        "enableInfiniteRenderLoopDetection",
        "enableFastAddPropertiesInDiffing",
        "enableViewTransition",
        "enableScrollEndPolyfill",
        "enableFragmentRefs",
        "enableFragmentRefsScrollIntoView",
        "enableAsyncDebugInfo",
        "enableInternalInstanceMap",
    ]
    missing = []
    for flag in required_flags:
        if f"export const {flag}: boolean = __VARIANT__;" not in content:
            missing.append(flag)
    assert not missing, (
        f"Existing __VARIANT__ flags missing or changed: {missing}"
    )


# [static] pass_to_pass
def test_file_structure_preserved():
    """File must retain @flow strict annotation and ES module export syntax."""
    content = _read_target()
    assert "@flow strict" in content, (
        "File is missing '@flow strict' annotation — file structure changed"
    )
    assert "export const" in content, (
        "File is missing 'export const' declarations — file structure changed"
    )


# [static] pass_to_pass
def test_hardcoded_section_comment_preserved():
    """The TODO warning comment about hardcoded flags must be preserved."""
    content = _read_target()
    assert "TODO: These flags are hard-coded" in content, (
        "TODO comment about hardcoded flags was removed — documentation lost"
    )
    assert "don" in content and "want to add more hardcoded ones" in content, (
        "Warning comment 'don't want to add more hardcoded ones' was removed"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — React CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_yarn_flags():
    """React feature flags validation passes (pass_to_pass).

    Runs yarn flags which validates all feature flag configurations,
    including the ReactFeatureFlags.www-dynamic.js file being modified.
    """
    r = subprocess.run(
        ["yarn", "flags"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"yarn flags failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_yarn_lint():
    """React codebase linting passes (pass_to_pass).

    Runs yarn lint to ensure all JS files pass ESLint checks.
    """
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"yarn lint failed:\n{r.stderr[-500:]}"
