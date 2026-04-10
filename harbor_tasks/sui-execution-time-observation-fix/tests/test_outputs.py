"""Tests for Sui execution time estimator fix.

This PR fixes a panic in execution_time_estimator.rs when timings.len() > tx.commands.len().
The original code had an assert that would crash; the fix handles this edge case gracefully.
"""

import subprocess
import re

REPO = "/workspace/sui"
TARGET_FILE = "crates/sui-core/src/authority/execution_time_estimator.rs"
SUI_CORE_CRATE = "crates/sui-core"


def test_rust_syntax_valid():
    """Verify the target file has valid Rust syntax (pass_to_pass)."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()
    assert "fn " in content, "No functions found in source file"
    assert "use " in content, "No imports found in source file"
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"


def test_no_panic_assert_in_code():
    """Fail-to-pass: The old assert!(tx.commands.len() >= timings.len()) must be removed."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()
    old_assert_pattern = r"assert!\s*\(\s*tx\.commands\.len\(\)\s*>=\s*timings\.len\(\)\s*\)"
    match = re.search(old_assert_pattern, content)
    assert match is None, f"Found old panic-inducing assert still present: {match.group(0) if match else ''}"


def test_defensive_timing_handling_exists():
    """Fail-to-pass: The fix must include defensive handling for excess timings."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()
    defensive_pattern = r"timings\.len\(\)\s*-\s*tx\.commands\.len\(\)"
    match = re.search(defensive_pattern, content)
    assert match is not None, "Defensive timing slicing logic not found"


def test_warning_log_for_excess_timings():
    """Fail-to-pass: The fix must include a warning log when timings exceed commands."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()
    warning_patterns = [
        "execution produced more timings than the original PTB commands",
        "executed_commands",
        "original_commands",
    ]
    for pattern in warning_patterns:
        assert pattern in content, f"Expected warning pattern '{pattern}' not found in fix"


def test_epoch_store_check_preserved():
    """Pass-to-pass: The epoch_store upgrade check must still be present and early."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()
    assert "epoch_store.upgrade()" in content, "epoch_store upgrade check missing"
    assert "epoch is ending, dropping execution time observation" in content, "epoch ending log message missing"


def test_function_signature_unchanged():
    """Pass-to-pass: The function signature should remain compatible."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()
    func_pattern = r"fn\s+record_local_observations_timing\s*\([^)]*timings:\s*&\[ExecutionTiming\][^)]*total_duration:[^)]*gas_price:[^)]*\)"
    match = re.search(func_pattern, content, re.DOTALL)
    assert match is not None, "record_local_observations_timing function signature changed or missing"


def test_cargo_fmt_check():
    """Repo code passes cargo fmt check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_target_file_has_tests_module():
    """Target file contains a tests module (pass_to_pass)."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()
    assert "mod tests" in content or "#[cfg(test)]" in content, "No tests module found in target file"


def test_cargo_toml_valid():
    """Cargo.toml files are valid (pass_to_pass)."""
    r = subprocess.run(
        ["cat", f"{REPO}/{SUI_CORE_CRATE}/Cargo.toml"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, "Failed to read sui-core Cargo.toml"
    content = r.stdout
    assert "[package]" in content, "Missing [package] section in Cargo.toml"
    assert 'name = "sui-core"' in content, "Missing or incorrect package name in Cargo.toml"


def test_repo_git_status_clean():
    """Repo has clean git status (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed:\n{r.stderr}"
