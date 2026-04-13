"""AFTER: Behavioral tests (the improved version)

These tests actually execute the code and verify correct behavior.
They can reliably distinguish between the broken and fixed versions.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/sample_repo"


def _run_js(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    # Use .js extension to work with CommonJS modules
    script = Path(REPO) / "_eval_tmp.js"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# FAIL-TO-PASS: These tests MUST fail on the base commit (broken) and pass after fix

def test_average_returns_zero_for_empty_array():
    """calculateAverage returns 0 for empty array (was returning null)."""
    r = _run_js("""
const { calculateAverage } = require('./index.js');
const result = calculateAverage([]);
console.log(JSON.stringify({ result }));
""")
    assert r.returncode == 0, f"Execution failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    # The fix changes: return null -> return 0
    assert data["result"] == 0, f"Expected 0 for empty array, got {data['result']}"


def test_average_works_for_normal_arrays():
    """calculateAverage returns correct value for non-empty arrays."""
    r = _run_js("""
const { calculateAverage } = require('./index.js');
const result = calculateAverage([1, 2, 3, 4, 5]);
console.log(JSON.stringify({ result }));
""")
    assert r.returncode == 0, f"Execution failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["result"] == 3.0, f"Expected 3.0, got {data['result']}"


def test_sum_function_works():
    """calculateSum returns correct sum."""
    r = _run_js("""
const { calculateSum } = require('./index.js');
const result = calculateSum([1, 2, 3, 4, 5]);
console.log(JSON.stringify({ result }));
""")
    assert r.returncode == 0, f"Execution failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["result"] == 15, f"Expected 15, got {data['result']}"


# PASS-TO-PASS: These tests must pass on BOTH base and fix commits

def test_repo_lint():
    """Repo linting passes (pass_to_pass gate)."""
    r = subprocess.run(
        ["npm", "run", "lint"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed: {r.stderr}"


def test_repo_tests_pass():
    """Repo's own test suite passes (pass_to_pass gate)."""
    r = subprocess.run(
        ["npm", "test"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-500:]}"


# Static checks (structural verification)

def test_file_structure():
    """Required source files exist."""
    assert Path(f"{REPO}/index.js").exists()
    assert Path(f"{REPO}/package.json").exists()
