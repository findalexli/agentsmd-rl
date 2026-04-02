"""
Task: vscode-ci-rerun-gate-workflow-id
Repo: microsoft/vscode @ 76258864c3a7669bd0254946543fe317959d1960
PR:   306362

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
MODEL_FILE = f"{REPO}/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts"
WIDGET_FILE = f"{REPO}/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """TypeScript must compile without errors after the fix."""
    r = subprocess.run(
        ["npm", "run", "compile-check-ts-native"],
        cwd=REPO,
        capture_output=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural changes from the PR
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parse_workflow_run_id_exported():
    """parseWorkflowRunId must be exported from githubPullRequestCIModel.ts."""
    content = Path(MODEL_FILE).read_text()
    assert "export function parseWorkflowRunId" in content, (
        "parseWorkflowRunId must be exported; found 'function parseWorkflowRunId' but not "
        "'export function parseWorkflowRunId'"
    )


# [pr_diff] fail_to_pass
def test_parse_workflow_run_id_imported_in_widget():
    """ciStatusWidget.ts must import parseWorkflowRunId from the model module."""
    content = Path(WIDGET_FILE).read_text()
    import_lines = [
        line for line in content.splitlines()
        if "import" in line and "parseWorkflowRunId" in line
    ]
    assert import_lines, (
        "parseWorkflowRunId must be imported in ciStatusWidget.ts; no import statement found"
    )


# [pr_diff] fail_to_pass
def test_gate_condition_in_ci_widget():
    """The 'Rerun Check' action must be gated on parseWorkflowRunId returning non-undefined.

    Verifies that:
    1. parseWorkflowRunId is called with the check's detailsUrl
    2. The result is compared to undefined (gates the action)
    """
    content = Path(WIDGET_FILE).read_text()
    # Must call parseWorkflowRunId with a detailsUrl-like argument
    has_call = bool(re.search(r'parseWorkflowRunId\([^)]*detailsUrl[^)]*\)', content))
    assert has_call, (
        "ciStatusWidget.ts must call parseWorkflowRunId(element.check.detailsUrl) "
        "to gate the rerun action"
    )
    # The return value must be checked against undefined
    has_undefined_check = bool(re.search(
        r'parseWorkflowRunId\([^)]*\)\s*!==\s*undefined', content
    ))
    assert has_undefined_check, (
        "The result of parseWorkflowRunId(...) must be compared to undefined "
        "to gate the 'Rerun Check' action"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + behavioral verification
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_function_not_stub():
    """parseWorkflowRunId must contain real URL parsing logic for '/actions/runs/'."""
    content = Path(MODEL_FILE).read_text()
    fn_start = content.find("function parseWorkflowRunId")
    assert fn_start != -1, "parseWorkflowRunId function not found in githubPullRequestCIModel.ts"
    # Extract ~500 chars of function body
    fn_snippet = content[fn_start:fn_start + 500]
    # Must reference the GitHub Actions URL pattern
    has_url_logic = (
        "/actions/runs/" in fn_snippet
        or ("actions" in fn_snippet and "runs" in fn_snippet and "match" in fn_snippet)
    )
    assert has_url_logic, (
        "parseWorkflowRunId does not contain URL parsing logic for '/actions/runs/'; "
        "it appears to be a stub"
    )


# [static] pass_to_pass
def test_parse_workflow_run_id_behavior():
    """parseWorkflowRunId correctly extracts run IDs (or returns undefined) for diverse inputs.

    # AST-only because: TypeScript source; no ts-node available in the image.
    # Function body is extracted from the .ts file, type annotations stripped,
    # then executed as plain JavaScript via Node.js.
    """
    content = Path(MODEL_FILE).read_text()
    fn_start = content.find("function parseWorkflowRunId")
    assert fn_start != -1, "parseWorkflowRunId not found"

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
        (
            "'https://github.com/microsoft/vscode/actions/runs/12345/job/67890'",
            "12345",
        ),
        # URL without job segment
        (
            "'https://github.com/owner/repo/actions/runs/99999'",
            "99999",
        ),
        # Minimal run ID = 1
        (
            "'https://github.com/owner/repo/actions/runs/1'",
            "1",
        ),
        # Non-GitHub-Actions URL → undefined
        (
            "'https://example.com/ci/check/1'",
            "undefined",
        ),
        # Completely unrelated URL → undefined
        (
            "'https://circleci.com/gh/owner/repo/123'",
            "undefined",
        ),
        # Empty string → undefined
        ("''", "undefined"),
        # undefined input → undefined
        ("undefined", "undefined"),
    ]

    checks = "\n".join(
        f"var _r{i} = parseWorkflowRunId({inp}); "
        f"if (_r{i} !== {exp}) {{ "
        f"  process.stderr.write('FAIL case {i}: input={inp} expected={exp} got=' + _r{i} + '\\n'); "
        f"  process.exit(1); "
        f"}}"
        for i, (inp, exp) in enumerate(test_cases)
    )

    script = f"{fn_js}\n{checks}\nconsole.log('all passed');"

    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, (
        f"parseWorkflowRunId behavior test failed:\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )
