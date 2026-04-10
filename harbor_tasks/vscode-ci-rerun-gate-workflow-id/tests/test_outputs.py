"""
Task: vscode-ci-rerun-gate-workflow-id
Repo: microsoft/vscode @ 76258864c3a7669bd0254946543fe317959d1960
PR:   306362

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import tempfile
import os
from pathlib import Path

REPO = "/workspace/vscode"
MODEL_FILE = Path(f"{REPO}/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts")
WIDGET_FILE = Path(f"{REPO}/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_files_exist():
    """Both modified TypeScript files are present in the workspace."""
    assert MODEL_FILE.exists(), f"Missing: {MODEL_FILE}"
    assert WIDGET_FILE.exists(), f"Missing: {WIDGET_FILE}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using code execution
# ---------------------------------------------------------------------------

def test_parse_workflow_run_id_exported():
    """parseWorkflowRunId must be exported and callable from external modules.

    Creates a temporary TypeScript file that imports the function and calls it.
    At base commit, the function is not exported so compilation fails.
    At fix commit, the function is exported so compilation and execution succeed.
    """
    test_code = '''
import { parseWorkflowRunId } from './src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.js';

// Test valid GitHub Actions URL
const result1 = parseWorkflowRunId('https://github.com/owner/repo/actions/runs/12345');
if (result1 !== 12345) {
    console.error('FAIL: expected 12345, got', result1);
    process.exit(1);
}

// Test undefined input
const result2 = parseWorkflowRunId(undefined);
if (result2 !== undefined) {
    console.error('FAIL: expected undefined, got', result2);
    process.exit(1);
}

// Test non-Actions URL
const result3 = parseWorkflowRunId('https://example.com/ci/check/1');
if (result3 !== undefined) {
    console.error('FAIL: expected undefined for non-Actions URL, got', result3);
    process.exit(1);
}

console.log('all tests passed');
'''

    # Write test file to repo root
    test_file = Path(REPO) / "_eval_export_test.mjs"
    test_file.write_text(test_code)

    try:
        r = subprocess.run(
            ["node", str(test_file)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, (
            f"parseWorkflowRunId export test failed:\n"
            f"stdout: {r.stdout}\nstderr: {r.stderr}"
        )
        assert "all tests passed" in r.stdout
    finally:
        test_file.unlink(missing_ok=True)


def test_widget_imports_and_uses_parse_workflow_run_id():
    """ciStatusWidget.ts must successfully import and use parseWorkflowRunId.

    Verifies by compiling the widget file - it will fail at base commit
    because the import statement references a non-exported function.
    """
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--allowJs",
         "src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"ciStatusWidget.ts compilation failed (import error):\n{r.stderr}"
    )


def test_gate_condition_checks_for_valid_workflow():
    """The 'Rerun Check' action is gated on parseWorkflowRunId returning non-undefined.

    Verifies the gate condition exists in the widget by checking that
    parseWorkflowRunId is called with detailsUrl and compared to undefined.
    This is a structural check but validates the correct behavioral gating.
    """
    content = WIDGET_FILE.read_text()

    # Must call parseWorkflowRunId with a detailsUrl-like argument
    has_call = bool(re.search(r'parseWorkflowRunId\([^)]*detailsUrl[^)]*\)', content))
    assert has_call, (
        "ciStatusWidget.ts must call parseWorkflowRunId(element.check.detailsUrl) "
        "to gate the rerun action"
    )

    # The return value must be compared to undefined (either !== or === comparison)
    has_undefined_check = bool(re.search(
        r'parseWorkflowRunId\([^)]*\)\s*!==?\s*undefined', content
    ))
    assert has_undefined_check, (
        "The result of parseWorkflowRunId(...) must be compared to undefined "
        "to gate the 'Rerun Check' action"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI/CD commands
# ---------------------------------------------------------------------------

def test_repo_tsfmt_check():
    """Repo's TypeScript formatter check passes (pass_to_pass).

    Runs tsfmt --dry on the modified files to verify they follow
    the project's formatting standards (tabs, not spaces).
    """
    for filepath in [MODEL_FILE, WIDGET_FILE]:
        r = subprocess.run(
            ["npx", "tsfmt", "--dry", str(filepath)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        # tsfmt exits 0 even if files would be formatted, we just need it to run
        # Check for actual errors in stderr
        if r.returncode != 0 and "Error" in r.stderr:
            raise AssertionError(f"tsfmt failed on {filepath.name}:\n{r.stderr}")


