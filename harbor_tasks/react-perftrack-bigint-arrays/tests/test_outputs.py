"""
Task: react-perftrack-bigint-arrays
Repo: facebook/react @ e66ef6480ecd19c6885f2c06dec34fec1fdc0a98
PR:   35648

Arrays containing BigInt values must be classified as COMPLEX_ARRAY in
ReactPerformanceTrackProperties.js, preventing JSON.stringify crashes.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/react"

# Jest test file written to the repo's __tests__ dir so babel/flow stripping works.
_JEST_FILE_CONTENT = """\
/**
 * @jest-environment node
 */

import {addValueToProperties} from '../ReactPerformanceTrackProperties';

// fail_to_pass: pure-BigInt arrays must return 'Array' label, not JSON string
test('bigint_only_array_is_complex', () => {
  const cases = [
    [1n, 2n, 3n],
    [BigInt(0), BigInt(999)],
    [1n],
  ];
  for (const arr of cases) {
    const props = [];
    addValueToProperties('items', arr, props, 0, '');
    const entry = props.find(p => p[0].includes('items'));
    expect(entry && entry[1]).toBe('Array');
  }
});

// fail_to_pass: arrays mixing BigInt with other primitives must be COMPLEX
test('mixed_bigint_array_is_complex', () => {
  const cases = [
    [1, 2n, 3],
    ['x', 1n],
    [1n, true],
  ];
  for (const arr of cases) {
    const props = [];
    addValueToProperties('data', arr, props, 0, '');
    const entry = props.find(p => p[0].includes('data'));
    expect(entry && entry[1]).toBe('Array');
  }
});

// fail_to_pass: addValueToProperties must not throw for BigInt arrays
test('no_json_stringify_crash_on_bigint', () => {
  const bigintArrays = [
    [1n],
    [1n, 2n, 3n],
    [BigInt(Number.MAX_SAFE_INTEGER)],
  ];
  for (const arr of bigintArrays) {
    const props = [];
    expect(() => addValueToProperties('val', arr, props, 0, '')).not.toThrow();
  }
});

// pass_to_pass: non-BigInt primitive arrays still serialize as JSON (regression)
test('primitive_array_still_serialized', () => {
  const cases = [
    {arr: [1, 2, 3], expected: '[1,2,3]'},
    {arr: [true, false], expected: '[true,false]'},
    {arr: [42], expected: '[42]'},
  ];
  for (const {arr, expected} of cases) {
    const props = [];
    addValueToProperties('p', arr, props, 0, '');
    const entry = props.find(e => e[0].includes('p'));
    expect(entry && entry[1]).toBe(expected);
  }
});
"""

_jest_results_cache = None


def _run_jest_suite() -> dict:
    """Write Jest file to packages/shared/__tests__, run jest once, cache JSON results."""
    global _jest_results_cache
    if _jest_results_cache is not None:
        return _jest_results_cache

    test_file = Path(f"{REPO}/packages/shared/__tests__/_bigint_task_test.js")
    result_file = Path("/tmp/_bigint_jest_results.json")

    test_file.write_text(_JEST_FILE_CONTENT)
    try:
        subprocess.run(
            [
                "yarn", "jest",
                "--config", "scripts/jest/config.source.js",
                "--no-coverage", "--forceExit",
                "--json", "--outputFile", str(result_file),
                "--testPathPattern", "_bigint_task_test",
            ],
            cwd=REPO,
            capture_output=True,
            timeout=120,
            text=True,
        )
        if result_file.exists():
            _jest_results_cache = json.loads(result_file.read_text())
        else:
            _jest_results_cache = {"testResults": [], "success": False}
    except Exception as e:
        _jest_results_cache = {"testResults": [], "success": False, "_exception": str(e)}
    finally:
        test_file.unlink(missing_ok=True)
        if result_file.exists():
            result_file.unlink()

    return _jest_results_cache


def _assert_jest_test_passed(test_name: str):
    results = _run_jest_suite()
    for file_result in results.get("testResults", []):
        for test in file_result.get("testResults", []):
            if test.get("title") == test_name:
                if test.get("status") == "passed":
                    return
                msgs = "\n".join(test.get("failureMessages", ["(no message)"]))
                pytest.fail(f"{test_name} FAILED:\n{msgs}")
    # Test not found — jest likely crashed at import (syntax/module error)
    err = results.get("_exception", "")
    file_results = results.get("testResults", [])
    console_out = ""
    if file_results:
        console_out = file_results[0].get("console", "")
    pytest.fail(
        f"Jest test '{test_name}' not found — jest may have crashed at import.\n"
        f"Exception: {err}\nConsole: {str(console_out)[:500]}\n"
        f"testResults count: {len(file_results)}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — BigInt classification fix
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bigint_only_array_is_complex():
    """Pure-BigInt arrays like [1n, 2n] must return 'Array' label, not JSON string."""
    _assert_jest_test_passed("bigint_only_array_is_complex")


# [pr_diff] fail_to_pass
def test_mixed_bigint_array_is_complex():
    """Arrays mixing BigInt with other types must return 'Array', not JSON string."""
    _assert_jest_test_passed("mixed_bigint_array_is_complex")


# [pr_diff] fail_to_pass
def test_no_json_stringify_crash_on_bigint():
    """addValueToProperties must not throw TypeError when array contains BigInt."""
    _assert_jest_test_passed("no_json_stringify_crash_on_bigint")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_primitive_array_still_serialized():
    """Non-BigInt primitive arrays must still be JSON-serialized (fix must not regress)."""
    _assert_jest_test_passed("primitive_array_still_serialized")
