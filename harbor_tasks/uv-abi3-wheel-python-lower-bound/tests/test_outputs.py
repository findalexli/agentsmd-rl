"""
Task: uv-abi3-wheel-python-lower-bound
Repo: astral-sh/uv @ 17afca33e9d7d678a1e00df280247eed39d8231d
PR:   18536

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import shutil
import re
from pathlib import Path

REPO = "/repo"
TARGET = "crates/uv-distribution-types/src/prioritized_distribution.rs"
TARGET_PATH = Path(REPO) / TARGET

# ---------------------------------------------------------------------------
# Injected Rust tests — compiled and run in a single cargo test invocation
# ---------------------------------------------------------------------------
INJECTED_TESTS = '''
    #[test]
    fn test_abi3_lower_bound_injected() {
        // cp39-abi3: CPython >= 3.9
        assert_python_markers(
            "pkg-1.0-cp39-abi3-any.whl",
            "python_full_version >= '3.9' and platform_python_implementation == 'CPython'",
        );
        // cp312-abi3: CPython >= 3.12
        assert_python_markers(
            "pkg-1.0-cp312-abi3-any.whl",
            "python_full_version >= '3.12' and platform_python_implementation == 'CPython'",
        );
        // cp310-abi3: CPython >= 3.10
        assert_python_markers(
            "pkg-1.0-cp310-abi3-any.whl",
            "python_full_version >= '3.10' and platform_python_implementation == 'CPython'",
        );
    }

    #[test]
    fn test_abi3_major_only_injected() {
        // cp3-abi3: CPython >= 3
        assert_python_markers(
            "pkg-1.0-cp3-abi3-any.whl",
            "python_full_version >= '3' and platform_python_implementation == 'CPython'",
        );
    }

    #[test]
    fn test_abi3_platform_injected() {
        // abi3 + manylinux platform
        assert_implied_markers(
            "pkg-1.0-cp39-abi3-manylinux_2_28_x86_64.whl",
            "python_full_version >= '3.9' and platform_python_implementation == 'CPython' and sys_platform == 'linux' and platform_machine == 'x86_64'",
        );
        // abi3 + different python version, same platform
        assert_implied_markers(
            "pkg-1.0-cp311-abi3-manylinux_2_28_x86_64.whl",
            "python_full_version >= '3.11' and platform_python_implementation == 'CPython' and sys_platform == 'linux' and platform_machine == 'x86_64'",
        );
    }

    #[test]
    fn test_non_abi3_exact_injected() {
        // cp39-cp39 (non-abi3): exact 3.9.*
        assert_python_markers(
            "pkg-1.0-cp39-cp39-any.whl",
            "python_full_version >= '3.9' and python_full_version < '3.10' and platform_python_implementation == 'CPython'",
        );
        // py3-none (pure python): exact 3.*
        assert_python_markers(
            "pkg-1.0-py3-none-any.whl",
            "python_full_version >= '3' and python_full_version < '4'",
        );
        // cp311-cp311 (non-abi3): exact 3.11.*
        assert_python_markers(
            "pkg-1.0-cp311-cp311-any.whl",
            "python_full_version >= '3.11' and python_full_version < '3.12' and platform_python_implementation == 'CPython'",
        );
    }
'''

# ---------------------------------------------------------------------------
# Single cargo test run — inject all tests, compile once, cache results
# ---------------------------------------------------------------------------
_cargo_cache = {}


def _run_all_cargo_tests():
    """Inject Rust test functions, run cargo test once, return cached results."""
    if _cargo_cache:
        return _cargo_cache

    backup = TARGET_PATH.with_suffix(".rs.bak")
    shutil.copy2(TARGET_PATH, backup)
    try:
        content = TARGET_PATH.read_text()
        # Insert before the last closing brace (end of mod tests block)
        last_brace = content.rfind("}")
        assert last_brace != -1, "Could not find closing brace in source"
        patched = content[:last_brace] + INJECTED_TESTS + "\n" + content[last_brace:]
        TARGET_PATH.write_text(patched)

        r = subprocess.run(
            [
                "cargo", "test", "--no-fail-fast",
                "-p", "uv-distribution-types", "--",
                "test_abi3_lower_bound_injected",
                "test_abi3_major_only_injected",
                "test_abi3_platform_injected",
                "test_non_abi3_exact_injected",
                "test_implied_python_markers",
                "test_implied_markers",
            ],
            cwd=REPO, capture_output=True, timeout=600,
        )
        _cargo_cache["stdout"] = r.stdout.decode(errors="replace")
        _cargo_cache["stderr"] = r.stderr.decode(errors="replace")
        _cargo_cache["returncode"] = r.returncode
    finally:
        shutil.move(str(backup), str(TARGET_PATH))

    return _cargo_cache


def _assert_rust_test_passed(test_name: str):
    """Assert that a specific Rust test passed in the cargo test output."""
    results = _run_all_cargo_tests()
    stdout = results["stdout"]
    stderr = results["stderr"]

    # cargo test output: "test tests::test_name ... ok" or "... FAILED"
    pattern = rf"test\s+tests::{re.escape(test_name)}\s+\.\.\.\s+(\w+)"
    m = re.search(pattern, stdout)
    if m:
        status = m.group(1)
        assert status == "ok", (
            f"Rust test {test_name} FAILED:\n{stdout[-3000:]}\n{stderr[-3000:]}"
        )
    else:
        # Test not found in output — likely a compilation error
        assert False, (
            f"Rust test {test_name} not found in output "
            f"(compilation error?):\n{stderr[-3000:]}"
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified crate must compile without errors."""
    # Uses the cached cargo test run — if it compiled, this passes.
    # If compilation failed, stderr will contain the error.
    results = _run_all_cargo_tests()
    stderr = results["stderr"]
    # Compilation errors produce "error[E" in stderr
    assert "error[E" not in stderr, (
        f"cargo compilation failed:\n{stderr[-3000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_abi3_lower_bound_markers():
    """abi3 wheels (cp39-abi3, cp312-abi3, cp310-abi3) produce >= version markers."""
    _assert_rust_test_passed("test_abi3_lower_bound_injected")


# [pr_diff] fail_to_pass
def test_abi3_major_only_tag():
    """abi3 wheel with major-only python tag (cp3-abi3) produces >= major version."""
    _assert_rust_test_passed("test_abi3_major_only_injected")


# [pr_diff] fail_to_pass
def test_abi3_with_platform_markers():
    """abi3 wheel with platform-specific tags produces correct combined >= markers."""
    _assert_rust_test_passed("test_abi3_platform_injected")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_non_abi3_exact_match():
    """Non-abi3 wheels still use exact version markers (==*)."""
    _assert_rust_test_passed("test_non_abi3_exact_injected")


# [repo_tests] pass_to_pass
def test_existing_implied_marker_tests():
    """Existing test_implied_python_markers and test_implied_markers pass."""
    _assert_rust_test_passed("test_implied_python_markers")
    _assert_rust_test_passed("test_implied_markers")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 17afca33e9d7d678a1e00df280247eed39d8231d
def test_no_forbidden_patterns_in_changed_function():
    """implied_python_markers must not use .unwrap(), panic!, unreachable!, unsafe, or clippy ignores."""
    content = TARGET_PATH.read_text()

    start = content.find("fn implied_python_markers(")
    assert start != -1, "Function implied_python_markers not found"

    # Extract function body by matching braces
    brace_count = 0
    in_func = False
    end = start
    for i in range(start, len(content)):
        if content[i] == '{':
            brace_count += 1
            in_func = True
        elif content[i] == '}':
            brace_count -= 1
            if in_func and brace_count == 0:
                end = i + 1
                break

    func_body = content[start:end]

    # CLAUDE.md line 7: AVOID panic!, unreachable!, .unwrap(), unsafe code, clippy ignores
    forbidden = {
        ".unwrap()": ".unwrap()",
        "panic!": "panic!(",
        "unreachable!": "unreachable!(",
        "unsafe block": "unsafe {",
        "#[allow(clippy": "#[allow(clippy",
    }
    for label, pattern in forbidden.items():
        assert pattern not in func_body, (
            f"Found {label} in implied_python_markers — "
            f"CLAUDE.md line 7: AVOID panic!, unreachable!, .unwrap(), unsafe, clippy ignores"
        )
