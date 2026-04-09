"""
Task: react-perf-track-typeof-crash
Repo: facebook/react @ e32c1261219a9d665f392a4799b8a24ea326f1a1

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: ReactPerformanceTrackProperties.js uses Flow type annotations and
cannot be executed directly in Node.js without a build step.
All checks are AST-only (string-based source inspection).
# AST-only because: file uses Flow type annotations requiring Babel/Hermes transpilation
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET_FILE = f"{REPO}/packages/shared/ReactPerformanceTrackProperties.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """ReactPerformanceTrackProperties.js must exist and be readable."""
    # Flow type annotations require transpilation; we verify file exists and
    # has valid structure via AST checks in other tests.
    assert Path(TARGET_FILE).exists(), f"File not found: {TARGET_FILE}"
    src = Path(TARGET_FILE).read_text()
    # Basic sanity: file should have exports and not be empty
    assert "export function" in src, "File missing expected exports"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — ensure fix doesn't break existing tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_react_perf_track():
    """React PerformanceTrack tests pass (pass_to_pass).

    Runs the ReactPerformanceTrack test suite to ensure the modified code
    doesn't break existing functionality.
    """
    r = subprocess.run(
        ["yarn", "test", "--ci", "ReactPerformanceTrack", "--reporter=summary"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"ReactPerformanceTrack tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_flow():
    """Repo Flow typecheck passes on shared package (pass_to_pass).

    Ensures the Flow type annotations in packages/shared/ are valid.
    """
    r = subprocess.run(
        ["yarn", "flow", "check", "packages/shared/", "--max-warnings", "0"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Flow may exit 0 on success or 2 on type errors
    if r.returncode not in (0, 2):
        assert False, f"Flow check crashed:\n{r.stderr[-500:]}"
    # Check for actual type errors in output
    if "Error:" in r.stdout or "Found " in r.stdout and "error" in r.stdout.lower():
        # Only fail if there are errors in our target file
        if "ReactPerformanceTrackProperties" in r.stdout:
            assert False, f"Flow type errors in ReactPerformanceTrackProperties:\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo ESLint checks pass (pass_to_pass).

    Runs the repo's linting to ensure code style and patterns are valid.
    """
    r = subprocess.run(
        ["yarn", "lint", "packages/shared/ReactPerformanceTrackProperties.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"ESLint check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_safe_reader_function_defined():
    """readReactElementTypeof helper function must be defined in the file.

    The fix introduces this function to safely access $$typeof on arbitrary
    objects, including cross-origin opaque proxies that throw on property access.
    """
    # AST-only because: file uses Flow type annotations requiring transpilation
    src = Path(TARGET_FILE).read_text()
    assert "function readReactElementTypeof" in src, (
        "readReactElementTypeof function not found — the fix must add this "
        "safe accessor helper"
    )


# [pr_diff] fail_to_pass
def test_safe_reader_uses_in_operator():
    """readReactElementTypeof must gate access with 'in' operator check.

    The 'in' operator does NOT invoke getters (unlike direct property access),
    so it is safe to use on cross-origin objects. Direct access like
    value.$$typeof would throw a SecurityError on cross-origin windows.
    """
    # AST-only because: file uses Flow type annotations requiring transpilation
    src = Path(TARGET_FILE).read_text()
    assert "'$$typeof' in value" in src, (
        "Missing '$$typeof' in value check — the fix must use the 'in' operator "
        "to avoid triggering getter traps on cross-origin objects"
    )


# [pr_diff] fail_to_pass
def test_safe_reader_uses_has_own_property():
    """readReactElementTypeof must use hasOwnProperty.call to avoid prototype pollution."""
    # AST-only because: file uses Flow type annotations requiring transpilation
    src = Path(TARGET_FILE).read_text()
    assert "hasOwnProperty.call(value, '$$typeof')" in src, (
        "Missing hasOwnProperty.call(value, '$$typeof') — must check own property "
        "to prevent prototype-inherited $$typeof from being used"
    )


# [pr_diff] fail_to_pass
def test_add_value_uses_safe_reader():
    """addValueToProperties must use readReactElementTypeof instead of direct access.

    Old: value.$$typeof === REACT_ELEMENT_TYPE  (throws on cross-origin objects)
    New: readReactElementTypeof(value) === REACT_ELEMENT_TYPE  (safe)
    """
    # AST-only because: file uses Flow type annotations requiring transpilation
    src = Path(TARGET_FILE).read_text()
    assert "value.$$typeof === REACT_ELEMENT_TYPE" not in src, (
        "Direct value.$$typeof access still present — must be replaced with "
        "readReactElementTypeof(value)"
    )
    assert "readReactElementTypeof(value) === REACT_ELEMENT_TYPE" in src, (
        "Safe accessor readReactElementTypeof(value) not used in addValueToProperties"
    )


# [pr_diff] fail_to_pass
def test_add_object_diff_uses_safe_reader():
    """addObjectDiffToProperties must use readReactElementTypeof for both $$typeof comparisons.

    Old: prevValue.$$typeof === nextValue.$$typeof
    New: readReactElementTypeof(prevValue) === readReactElementTypeof(nextValue)
    """
    # AST-only because: file uses Flow type annotations requiring transpilation
    src = Path(TARGET_FILE).read_text()
    assert "prevValue.$$typeof === nextValue.$$typeof" not in src, (
        "Direct prevValue.$$typeof === nextValue.$$typeof still present in "
        "addObjectDiffToProperties — must use safe reader"
    )
    assert "readReactElementTypeof(prevValue)" in src, (
        "readReactElementTypeof(prevValue) not found in addObjectDiffToProperties"
    )
    assert "readReactElementTypeof(nextValue)" in src, (
        "readReactElementTypeof(nextValue) not found in addObjectDiffToProperties"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_helper_defined_before_first_use():
    """readReactElementTypeof must be defined before addValueToProperties uses it."""
    # AST-only because: file uses Flow type annotations requiring transpilation
    src = Path(TARGET_FILE).read_text()
    assert "function readReactElementTypeof" in src, "Helper function not present"
    assert "export function addValueToProperties" in src, "addValueToProperties not found"
    read_pos = src.index("function readReactElementTypeof")
    add_val_pos = src.index("export function addValueToProperties")
    assert read_pos < add_val_pos, (
        f"readReactElementTypeof (pos {read_pos}) must be defined before "
        f"addValueToProperties (pos {add_val_pos})"
    )


# [static] pass_to_pass
def test_helper_used_in_multiple_locations():
    """readReactElementTypeof must be used in at least 3 places (definition + 2 call sites)."""
    # AST-only because: file uses Flow type annotations requiring transpilation
    src = Path(TARGET_FILE).read_text()
    count = src.count("readReactElementTypeof")
    assert count >= 3, (
        f"Expected readReactElementTypeof to appear ≥3 times (definition + call in "
        f"addValueToProperties + call in addObjectDiffToProperties), found {count}"
    )
