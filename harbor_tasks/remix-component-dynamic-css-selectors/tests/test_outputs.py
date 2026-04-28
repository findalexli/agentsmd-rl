"""Tests for remix-run/remix dynamic CSS selectors fix (PR #11034).

Verifies that the style processing library correctly handles undefined values
for nested CSS selectors and at-rules, skipping them instead of throwing.
"""

import json
import subprocess
import sys

REPO = '/workspace/remix'
RUNNER = '/tests/test_style_runner.ts'


def _run_runner():
    """Run the TypeScript test runner and return parsed results."""
    r = subprocess.run(
        ['npx', 'tsx', RUNNER],
        capture_output=True,
        text=True,
        timeout=30,
        cwd='/tmp',
    )
    if r.returncode != 0:
        raise RuntimeError(f'Test runner failed (exit {r.returncode}):\nSTDOUT: {r.stdout}\nSTDERR: {r.stderr}')
    # Last line should be the JSON array
    lines = [l for l in r.stdout.strip().split('\n') if l.strip()]
    if not lines:
        raise RuntimeError(f'No output from test runner. STDERR: {r.stderr}')
    return json.loads(lines[-1])


def test_normal_style_processing():
    """Basic style processing works correctly at base commit (pass_to_pass)."""
    results = _run_runner()
    entry = next(r for r in results if r['name'] == 'normal_style_processing')
    assert entry['passed'], f"Expected pass, got: {entry['details']}"


def test_undefined_nested_selector_no_throw():
    """processStyle skips undefined nested selector values instead of throwing TypeError."""
    results = _run_runner()
    entry = next(r for r in results if r['name'] == 'undefined_nested_selector_no_throw')
    assert entry['passed'], f"Expected pass, got: {entry['details']}"


def test_undefined_at_rule_no_throw():
    """processStyle skips undefined at-rule values instead of throwing TypeError."""
    results = _run_runner()
    entry = next(r for r in results if r['name'] == 'undefined_at_rule_no_throw')
    assert entry['passed'], f"Expected pass, got: {entry['details']}"


def test_conditional_nested_selector_skip():
    """Undefined nested selectors are absent from generated CSS output."""
    results = _run_runner()
    entry = next(r for r in results if r['name'] == 'conditional_nested_selector_skip')
    assert entry['passed'], f"Expected pass, got: {entry['details']}"


def test_conditional_at_rule_skip():
    """Undefined at-rules are absent from generated CSS output while defined ones remain."""
    results = _run_runner()
    entry = next(r for r in results if r['name'] == 'conditional_at_rule_skip')
    assert entry['passed'], f"Expected pass, got: {entry['details']}"


def test_mixed_undefined_defined_nested():
    """Mixing undefined and defined nested selectors produces correct output."""
    results = _run_runner()
    entry = next(r for r in results if r['name'] == 'mixed_undefined_defined_nested')
    assert entry['passed'], f"Expected pass, got: {entry['details']}"


def test_array_not_treated_as_record():
    """Array values for nested selectors are skipped, not iterated."""
    results = _run_runner()
    entry = next(r for r in results if r['name'] == 'array_not_treated_as_record')
    assert entry['passed'], f"Expected pass, got: {entry['details']}"


def test_null_nested_selector_skip():
    """Null values for nested selectors are silently skipped."""
    results = _run_runner()
    entry = next(r for r in results if r['name'] == 'null_nested_selector_skip')
    assert entry['passed'], f"Expected pass, got: {entry['details']}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")