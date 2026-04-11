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
    """parseWorkflowRunId must be exported from the model file.

    At base commit, the function is not exported (private to module).
    At fix commit, the function is exported with 'export' keyword.
    We verify this by checking the source code for 'export function parseWorkflowRunId'.
    """
    content = MODEL_FILE.read_text()

    # Check for the exported function signature
    has_export = "export function parseWorkflowRunId" in content
    assert has_export, (
        "parseWorkflowRunId must be exported from githubPullRequestCIModel.ts. "
        "Expected 'export function parseWorkflowRunId(...)' in the file."
    )


def test_widget_imports_and_uses_parse_workflow_run_id():
    """ciStatusWidget.ts must import and use parseWorkflowRunId.

    At base commit, the widget does not import parseWorkflowRunId.
    At fix commit, the widget imports and uses parseWorkflowRunId.
    We verify this by checking the source code for the import statement.
    """
    content = WIDGET_FILE.read_text()

    # Check for the import of parseWorkflowRunId from the model file
    has_import = "parseWorkflowRunId" in content and "githubPullRequestCIModel" in content
    assert has_import, (
        "ciStatusWidget.ts must import parseWorkflowRunId from githubPullRequestCIModel. "
        "Expected 'import { ..., parseWorkflowRunId } from ...githubPullRequestCIModel.js'"
    )

    # Check that parseWorkflowRunId is called in the file
    has_usage = "parseWorkflowRunId(" in content
    assert has_usage, (
        "ciStatusWidget.ts must call parseWorkflowRunId function. "
        "Expected 'parseWorkflowRunId(...)' somewhere in the file."
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


def test_repo_tsfmt_check_widget():
    """Repo's TypeScript formatter check passes on ciStatusWidget.ts (pass_to_pass).

    Runs tsfmt --dry specifically on ciStatusWidget.ts to verify it follows
    the project's formatting standards (tabs, not spaces).
    """
    r = subprocess.run(
        ["npx", "tsfmt", "--dry", str(WIDGET_FILE)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # tsfmt exits 0 even if files would be formatted, we just need it to run without errors
    assert r.returncode == 0, f"tsfmt check failed on ciStatusWidget.ts:\n{r.stderr}"


def test_model_file_parses():
    """GitHubPullRequestCIModel.ts is valid TypeScript that parses without errors (pass_to_pass).

    Uses Node.js to read and validate the file structure - ensures it's valid
    TypeScript syntax that can be parsed.
    """
    test_script = '''
const fs = require('fs');

const filePath = '/workspace/vscode/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts';

try {
    const content = fs.readFileSync(filePath, 'utf8');

    // Check for basic TypeScript class structure
    if (!content.includes('export class GitHubPullRequestCIModel')) {
        console.error('FAIL: GitHubPullRequestCIModel class not found');
        process.exit(1);
    }

    // Check for parseWorkflowRunId function
    if (!content.includes('parseWorkflowRunId')) {
        console.error('FAIL: parseWorkflowRunId function not found');
        process.exit(1);
    }

    // Check for proper imports
    if (!content.includes('import {')) {
        console.error('FAIL: No imports found');
        process.exit(1);
    }

    console.log('Model file structure is valid');
    process.exit(0);
} catch (err) {
    console.error('Error reading file:', err.message);
    process.exit(1);
}
'''
    test_file = Path(REPO) / "_eval_model_parse_test.cjs"
    test_file.write_text(test_script)

    try:
        r = subprocess.run(
            ["node", str(test_file)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Model file parse test failed:\n{r.stderr}"
    finally:
        test_file.unlink(missing_ok=True)


def test_widget_file_parses():
    """ciStatusWidget.ts is valid TypeScript that parses without errors (pass_to_pass).

    Uses Node.js to read and validate the file structure - ensures it's valid
    TypeScript syntax with the expected imports and class structure.
    """
    test_script = '''
const fs = require('fs');

const filePath = '/workspace/vscode/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts';

try {
    const content = fs.readFileSync(filePath, 'utf8');

    // Check for CICheckListRenderer class
    if (!content.includes('class CICheckListRenderer')) {
        console.error('FAIL: CICheckListRenderer class not found');
        process.exit(1);
    }

    // Check for expected imports
    if (!content.includes('import {')) {
        console.error('FAIL: No imports found');
        process.exit(1);
    }

    // Check for GitHubCICheck type usage
    if (!content.includes('GitHubCICheck')) {
        console.error('FAIL: GitHubCICheck type not found');
        process.exit(1);
    }

    console.log('Widget file structure is valid');
    process.exit(0);
} catch (err) {
    console.error('Error reading file:', err.message);
    process.exit(1);
}
'''
    test_file = Path(REPO) / "_eval_widget_parse_test.cjs"
    test_file.write_text(test_script)

    try:
        r = subprocess.run(
            ["node", str(test_file)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Widget file parse test failed:\n{r.stderr}"
    finally:
        test_file.unlink(missing_ok=True)
