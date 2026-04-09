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
# Pass-to-pass (static/pr_diff) — behavioral verification
# ---------------------------------------------------------------------------

def test_parse_workflow_run_id_behavior():
    """parseWorkflowRunId correctly extracts run IDs or returns undefined for diverse inputs.

    Extracts the function body from the .ts file, strips TypeScript annotations,
    and executes as plain JavaScript via Node.js to verify runtime behavior.
    """
    content = MODEL_FILE.read_text()
    fn_start = content.find("function parseWorkflowRunId")
    assert fn_start != -1, "parseWorkflowRunId not found in githubPullRequestCIModel.ts"

    # Extract brace-balanced function body
    brace_count = 0
    fn_end = fn_start
    for i, ch in enumerate(content[fn_start:], fn_start):
        if ch == '{':
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0:
                fn_end = i + 1
                break

    fn_text = content[fn_start:fn_end]

    # Strip TypeScript type annotations to get executable JS
    fn_js = re.sub(r':\s*(?:string|number)(?:\s*\|\s*undefined)?', '', fn_text)
    fn_js = fn_js.replace('export ', '')

    # Test cases: (input_js_expr, expected_js_value)
    test_cases = [
        # Standard GitHub Actions URL with job segment
        ("'https://github.com/microsoft/vscode/actions/runs/12345/job/67890'", "12345"),
        # URL without job segment
        ("'https://github.com/owner/repo/actions/runs/99999'", "99999"),
        # Minimal run ID = 1
        ("'https://github.com/owner/repo/actions/runs/1'", "1"),
        # Large run ID
        ("'https://github.com/org/project/actions/runs/9876543210'", "9876543210"),
        # Non-GitHub-Actions URL -> undefined
        ("'https://example.com/ci/check/1'", "undefined"),
        # CircleCI URL -> undefined
        ("'https://circleci.com/gh/owner/repo/123'", "undefined"),
        # URL with /actions/ but no /runs/ -> undefined
        ("'https://github.com/owner/repo/actions/workflows/ci.yml'", "undefined"),
        # Empty string -> undefined
        ("''", "undefined"),
        # undefined input -> undefined
        ("undefined", "undefined"),
    ]

    checks = "\n".join(
        f"var _r{i} = parseWorkflowRunId({inp}); "
        f"if (String(_r{i}) !== String({exp})) {{ "
        f"  process.stderr.write('FAIL case {i}: got=' + _r{i} + ' expected={exp}\\n'); "
        f"  process.exit(1); "
        f"}}"
        for i, (inp, exp) in enumerate(test_cases)
    )

    script = f"{fn_js}\n{checks}\nconsole.log('all passed');"

    # Write to temp file and execute via Node
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False)
    tmp.write(script)
    tmp.close()
    try:
        r = subprocess.run(
            ["node", tmp.name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert r.returncode == 0, (
            f"parseWorkflowRunId behavior test failed:\n"
            f"stdout: {r.stdout}\nstderr: {r.stderr}"
        )
        assert "all passed" in r.stdout
    finally:
        os.unlink(tmp.name)


def test_model_compiles_cleanly():
    """The model TypeScript file compiles without errors."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck",
         "src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Model file compilation failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

def test_uses_tabs_not_spaces():
    """Modified code uses tabs for indentation, not spaces.

    Rule: 'We use tabs, not spaces.' (.github/copilot-instructions.md:72)
    Checks that all non-empty, non-import lines in both modified files use
    tab indentation rather than leading spaces.
    """
    for filepath in [MODEL_FILE, WIDGET_FILE]:
        content = filepath.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if not line or line == line.lstrip():
                continue  # blank or no indentation
            stripped = line.lstrip()
            # Skip JSDoc/block comment lines (` * ...`, ` *---*/`, etc.)
            if stripped.startswith('*'):
                continue
            # Line is indented — must start with tab, not spaces
            assert line[0] == '\t', (
                f"{filepath.name}:{i} uses space indentation: {line!r}"
            )
