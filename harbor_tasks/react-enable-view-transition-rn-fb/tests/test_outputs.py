"""
Task: react-enable-view-transition-rn-fb
Repo: facebook/react @ b4546cd0d4db2b913d8e7503bee86e1844073b2e
PR:   36106

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
FLAG_NATIVE_FB = f"{REPO}/packages/shared/forks/ReactFeatureFlags.native-fb.js"
FLAG_TEST_RN = f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js"
FLAG_TEST_WWW = f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js"


def _get_flag_value(filepath: str, flag_name: str) -> tuple[bool, str]:
    """Extract flag value from a JS file using regex.
    
    Returns (value, error_message). If error_message is not empty, the extraction failed.
    """
    content = Path(filepath).read_text()
    
    # Find the line with the flag declaration
    # Matches patterns like:
    #   export const enableViewTransition: boolean = true;
    #   export const enableViewTransition = true;
    #   const enableViewTransition: boolean = true;
    pattern = rf'^\s*export\s+const\s+{flag_name}(?::\s*\w+)?\s*=\s*(\w+)\s*;'
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        # Try without export keyword
        pattern2 = rf'^\s*const\s+{flag_name}(?::\s*\w+)?\s*=\s*(\w+)\s*;'
        match = re.search(pattern2, content, re.MULTILINE)
    
    if not match:
        return False, f"Could not find {flag_name} declaration in {filepath}"
    
    value_str = match.group(1)
    if value_str == 'true':
        return True, ""
    elif value_str == 'false':
        return False, ""
    elif value_str == '__PROFILE__':
        # __PROFILE__ is a placeholder, treat as boolean (false for testing)
        return False, ""
    elif value_str == '__VARIANT__':
        return False, ""
    else:
        return False, f"Unknown value {value_str} for {flag_name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core flag changes via regex parsing
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enable_view_transition_native_fb():
    """enableViewTransition is true in ReactFeatureFlags.native-fb.js."""
    value, error = _get_flag_value(FLAG_NATIVE_FB, "enableViewTransition")
    assert not error, error
    assert value is True, f"enableViewTransition should be true in native-fb.js, got {value}"


# [pr_diff] fail_to_pass
def test_enable_view_transition_test_renderer_native_fb():
    """enableViewTransition is true in ReactFeatureFlags.test-renderer.native-fb.js."""
    value, error = _get_flag_value(FLAG_TEST_RN, "enableViewTransition")
    assert not error, error
    assert value is True, f"enableViewTransition should be true in test-renderer.native-fb.js, got {value}"


# [pr_diff] fail_to_pass
def test_enable_view_transition_test_renderer_www():
    """enableViewTransition is true in ReactFeatureFlags.test-renderer.www.js."""
    value, error = _get_flag_value(FLAG_TEST_WWW, "enableViewTransition")
    assert not error, error
    assert value is True, f"enableViewTransition should be true in test-renderer.www.js, got {value}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub: no collateral flag changes
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_unintended_flag_changes():
    """Other flags remain at their base-commit values — only enableViewTransition was changed."""
    flags_must_stay_false = [
        "enableGestureTransition",
        "enableSuspenseyImages",
        "enableYieldingBeforePassive",
        "enableThrottledScheduling",
    ]
    for filepath in [FLAG_NATIVE_FB, FLAG_TEST_RN, FLAG_TEST_WWW]:
        content = Path(filepath).read_text()
        for flag in flags_must_stay_false:
            m = re.search(
                rf'export const {flag}(?::\s*\w+)?\s*=\s*(\S+?)\s*;', content
            )
            if m:
                actual = m.group(1)
                assert actual == "false", (
                    f"{flag} should remain 'false' in {Path(filepath).name}, "
                    f"found: '{actual}' — only enableViewTransition should be changed"
                )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass on base and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo ESLint check
def test_repo_eslint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Shared package tests
def test_repo_shared_package_tests():
    """Shared package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=packages/shared", "--timeout=60"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Shared package tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Feature flags validation
def test_repo_flags_validation():
    """Feature flags validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flags"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flags validation failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Version check
def test_repo_version_check():
    """Version check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/version-check.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Version check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — React Transition tests
def test_repo_react_transition_tests():
    """React Transition tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=ReactTransition-test", "--timeout=60", "--passWithNoTests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"React Transition tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — React test-renderer tests
def test_repo_react_test_renderer_tests():
    """React test-renderer tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=test-renderer", "--timeout=60", "--passWithNoTests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"React test-renderer tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — React StartTransition tests
def test_repo_react_start_transition_tests():
    """React StartTransition tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=ReactStartTransition", "--timeout=60", "--passWithNoTests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"React StartTransition tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — React DOM ViewTransition tests
def test_repo_react_dom_view_transition_tests():
    """React DOM ViewTransition tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=ReactDOMViewTransition-test", "--timeout=60", "--passWithNoTests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"React DOM ViewTransition tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Agent-config derived (agent_config) — .claude/skills/feature-flags/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/feature-flags/SKILL.md:78 @ b4546cd0d4db2b913d8e7503bee86e1844073b2e
def test_all_fork_files_have_view_transition_enabled():
    """All three fork files must have enableViewTransition enabled (not just one).

    Rule: 'Missing fork files — New flags must be added to ALL fork files, not just the main one'
    Source: .claude/skills/feature-flags/SKILL.md line 78
    """
    files = {
        "native-fb.js": FLAG_NATIVE_FB,
        "test-renderer.native-fb.js": FLAG_TEST_RN,
        "test-renderer.www.js": FLAG_TEST_WWW,
    }
    failures = []
    for name, filepath in files.items():
        value, error = _get_flag_value(filepath, "enableViewTransition")
        if error:
            failures.append(f"{name}: error - {error}")
        elif value is not True:
            failures.append(f"{name}: value={value}")

    assert not failures, (
        "enableViewTransition must be true in ALL fork files. "
        "Failed: " + ", ".join(failures)
    )
