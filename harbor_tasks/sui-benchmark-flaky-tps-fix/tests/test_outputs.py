"""
Tests for sui-benchmark flaky TPS fix.

Fail-to-pass tests:
1. test_tps_calculation_uses_float_division - Verify TPS is calculated with floating-point precision
2. test_min_tps_threshold_lowered - Verify CI uses --min-tps 0.01 instead of 1
3. test_no_integer_division_in_tps - Verify old integer division pattern is removed

Pass-to-pass tests (repo_tests - actual CI commands):
1. test_repo_cargo_fmt - cargo fmt --check
2. test_repo_git_checks - scripts/git-checks.sh
3. test_repo_cargo_xlint - cargo xlint
4. test_repo_yaml_valid - Validate YAML syntax

Pass-to-pass tests (static - file content checks):
1. test_rust_syntax_valid - Basic Rust syntax validation
2. test_workflow_has_min_tps - Verify workflow has min-tps setting
"""

import subprocess
import re
import sys
import yaml

REPO = "/workspace/sui"


def test_tps_calculation_uses_float_division():
    """
    FAIL TO PASS: Verify that TPS calculation uses floating-point division.

    The bug was using integer division (num_txes / duration.as_secs()) which
    truncated to 0 for fractional TPS values. The fix should use as_secs_f64()
    and format to 2 decimal places.
    """
    driver_file = f"{REPO}/crates/sui-benchmark/src/drivers/mod.rs"

    with open(driver_file, 'r') as f:
        content = f.read()

    # Check that as_secs_f64() is used (the fix)
    assert "as_secs_f64()" in content, \
        "TPS calculation should use as_secs_f64() for floating-point precision"

    # Check that the calculation uses f64 cast and floating-point division
    assert "as f64 / duration_secs" in content, \
        "TPS calculation should cast to f64 for floating-point division"

    # Check that formatting with 2 decimal places is used
    assert '{:.2}' in content, \
        "TPS should be formatted to 2 decimal places"

    print("PASS: TPS calculation uses floating-point division with 2 decimal precision")


def test_min_tps_threshold_lowered():
    """
    FAIL TO PASS: Verify that --min-tps is lowered to 0.01 in CI workflow.

    The CI workflow was using --min-tps 1 which was too strict for slow runners.
    The fix changes it to 0.01 to avoid false negatives from borderline TPS values.
    """
    workflow_file = f"{REPO}/.github/workflows/rust.yml"

    with open(workflow_file, 'r') as f:
        content = f.read()

    # Check that --min-tps 0.01 is present
    assert "--min-tps 0.01" in content, \
        "CI workflow should use --min-tps 0.01 (not 1) for the benchmark smoke test"

    # Verify the old threshold is not present in the benchmark job context
    lines = content.split("\n")
    for line in lines:
        if 'min-tps' in line and 'bench' in line.lower():
            assert '0.01' in line, \
                f"Benchmark job should use --min-tps 0.01, found: {line.strip()}"

    print("PASS: CI workflow uses lowered --min-tps 0.01 threshold")


def test_no_integer_division_in_tps():
    """
    FAIL TO PASS: Verify that the old integer division pattern is gone.

    The original buggy code was:
        row.add_cell(Cell::new(self.num_success_txes / self.duration.as_secs()));

    This should be replaced with floating-point calculation.
    """
    driver_file = f"{REPO}/crates/sui-benchmark/src/drivers/mod.rs"

    with open(driver_file, 'r') as f:
        content = f.read()

    # Check that we're NOT using integer division for TPS
    bad_patterns = [
        "num_success_txes / self.duration.as_secs()",
        "num_success_cmds / self.duration.as_secs()",
    ]

    for pattern in bad_patterns:
        assert pattern not in content, \
            f"Found integer division pattern that should be fixed: {pattern}"

    print("PASS: No integer division in TPS calculation")


def test_rust_syntax_valid():
    """
    PASS TO PASS (static): Verify the Rust driver file has valid syntax patterns.

    This is a lightweight check that doesn't require full compilation.
    Validates that the file is parseable Rust code.
    """
    driver_file = f"{REPO}/crates/sui-benchmark/src/drivers/mod.rs"

    with open(driver_file, 'r') as f:
        content = f.read()

    # Basic syntax checks that would catch obvious errors
    # Check for balanced braces (excluding braces in strings/comments is complex,
    # so we just do a simple count for sanity check)
    open_braces = content.count("{" "}")
    close_braces = content.count("}" "}")

    # The difference should be small (accounting for string literals with braces)
    assert abs(open_braces - close_braces) <= 5, \
        f"Suspiciously unbalanced braces: {open_braces} open, {close_braces} close"

    # Check for balanced parentheses
    open_parens = content.count("(")
    close_parens = content.count(")")
    assert abs(open_parens - close_parens) <= 5, \
        f"Suspiciously unbalanced parentheses: {open_parens} open, {close_parens} close"

    # Check file has expected Rust structure
    assert "impl BenchmarkStats" in content, \
        "Should contain BenchmarkStats impl block"
    assert "pub fn to_table" in content, \
        "Should contain to_table method"
    assert "Cell::new" in content, \
        "Should use Cell::new for table construction"

    print("PASS: Rust syntax validation passed")


def test_workflow_has_min_tps():
    """
    PASS TO PASS (static): Verify the workflow file has proper min-tps setting.
    """
    workflow_file = f"{REPO}/.github/workflows/rust.yml"

    with open(workflow_file, 'r') as f:
        content = f.read()

    # Basic YAML structure checks
    # Check that the file starts with proper YAML marker or 'name:'
    lines = content.strip().split("\n")
    first_line = lines[0].strip()
    assert first_line.startswith("name:") or first_line.startswith("---"), \
        "YAML should start with 'name:' or '---'"

    # Check that min-tps is present in the workflow
    assert "min-tps" in content, \
        "Workflow should contain min-tps parameter"

    print("PASS: Workflow min-tps validation passed")


def test_repo_cargo_fmt():
    """
    PASS TO PASS (repo_tests): Verify code formatting passes (cargo fmt --check).

    This is the repo's CI formatting check that should pass on both
    base commit and after the fix.
    """
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr}\n{r.stdout}"
    print("PASS: cargo fmt --check passed")


def test_repo_git_checks():
    """
    PASS TO PASS (repo_tests): Run the repo's git checks script.

    Validates: no submodules, no case-insensitive filename conflicts,
    and no trailing whitespace errors in the latest commit.
    """
    r = subprocess.run(
        ["bash", "scripts/git-checks.sh"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Git checks failed:\n{r.stderr}\n{r.stdout}"
    print("PASS: scripts/git-checks.sh passed")


def test_repo_cargo_xlint():
    """
    PASS TO PASS (repo_tests): Run the repo's custom linter (cargo xlint).

    This is the repo's license/lint check used in CI.
    """
    r = subprocess.run(
        ["cargo", "xlint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo xlint failed:\n{r.stderr}\n{r.stdout}"
    print("PASS: cargo xlint passed")


def test_repo_yaml_valid():
    """
    PASS TO PASS (repo_tests): Validate that workflow YAML files are syntactically valid.
    """
    workflow_file = f"{REPO}/.github/workflows/rust.yml"

    # Validate YAML can be parsed
    with open(workflow_file, 'r') as f:
        yaml.safe_load(f)

    print("PASS: YAML syntax validation passed")


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_tps_calculation_uses_float_division,
        test_min_tps_threshold_lowered,
        test_no_integer_division_in_tps,
        test_rust_syntax_valid,
        test_workflow_has_min_tps,
        test_repo_cargo_fmt,
        test_repo_git_checks,
        test_repo_cargo_xlint,
        test_repo_yaml_valid,
    ]

    failed = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            failed.append((test.__name__, str(e)))
            print(f"FAIL: {test.__name__}: {e}")
        except Exception as e:
            failed.append((test.__name__, str(e)))
            print(f"ERROR: {test.__name__}: {e}")

    if failed:
        print(f"\n{len(failed)} test(s) failed:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed!")
        sys.exit(0)
