#!/usr/bin/env python3
"""Test outputs for sui timings crash fix."""

import subprocess
import sys
import re

REPO = "/workspace/sui"
TARGET_FILE = f"{REPO}/crates/sui-core/src/authority/execution_time_estimator.rs"


def read_target_file():
    with open(TARGET_FILE, 'r') as f:
        return f.read()


def test_crash_assertion_removed():
    content = read_target_file()
    bad_assertion = "assert!(tx.commands.len() >= timings.len())"
    if bad_assertion in content:
        raise AssertionError(f"Crash-inducing assertion still present: {bad_assertion}")
    print("PASS: Crash-inducing assertion removed")


def test_timings_trim_logic_exists():
    content = read_target_file()
    if "execution produced more timings than the original PTB commands" not in content:
        raise AssertionError("Missing warning message about extra timings")
    if not re.search(r"&?timings\[timings\.len\(\)\s*-\s*tx\.commands\.len\(\)\.\.\]", content):
        raise AssertionError("Missing timings trimming logic")
    print("PASS: Timings trimming logic present")


def test_early_return_preserved():
    content = read_target_file()
    func_match = re.search(r"fn record_local_observations_timing.*?^\s*}", content, re.DOTALL | re.MULTILINE)
    if not func_match:
        raise AssertionError("Could not find function")
    func_content = func_match.group(0)
    if "let Some(epoch_store) = self.epoch_store.upgrade()" not in func_content:
        raise AssertionError("Missing epoch_store upgrade check")
    if "epoch is ending, dropping execution time observation" not in func_content:
        raise AssertionError("Missing epoch ending debug message")
    print("PASS: Early return preserved")


def test_repo_rustfmt():
    """Repo's rustfmt check passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Rustfmt check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    print("PASS: Repo rustfmt check")


def test_repo_xlint():
    """Repo's xlint (license/workspace check) passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "xlint"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Xlint check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    print("PASS: Repo xlint check")


if __name__ == "__main__":
    tests = [
        test_crash_assertion_removed,
        test_timings_trim_logic_exists,
        test_early_return_preserved,
        test_repo_rustfmt,
        test_repo_xlint,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
