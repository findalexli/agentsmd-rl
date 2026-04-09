"""
Task: vscode-sessions-ci-rerun-action
Repo: microsoft/vscode @ 64e73b036669494bbc9a6904cf090b01a8d3bb1e
PR:   306347

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
FETCHER = f"{REPO}/src/vs/sessions/contrib/github/browser/fetchers/githubPRCIFetcher.ts"
MODEL = f"{REPO}/src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts"
WIDGET = f"{REPO}/src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts"

# AST-only (all checks): TypeScript source files cannot be executed without a
# full Node/tsc build environment; all checks use file content inspection.


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rerun_failed_jobs_method_in_fetcher():
    """GitHubPRCIFetcher must have an async rerunFailedJobs method calling the GitHub API."""
    src = Path(FETCHER).read_text()
    assert "async rerunFailedJobs" in src, "rerunFailedJobs method missing from fetcher"
    assert "rerun-failed-jobs" in src, "GitHub API endpoint 'rerun-failed-jobs' not used in fetcher"
    assert "/actions/runs/" in src, "API path must include /actions/runs/ in fetcher"


# [pr_diff] fail_to_pass
def test_rerun_failed_check_method_in_model():
    """GitHubPullRequestCIModel must have rerunFailedCheck that calls the fetcher and refreshes."""
    src = Path(MODEL).read_text()
    assert "async rerunFailedCheck" in src, "rerunFailedCheck method missing from model"
    assert "rerunFailedJobs" in src, "rerunFailedCheck must delegate to rerunFailedJobs"
    assert "refresh" in src, "Model must call refresh() after triggering rerun"


# [pr_diff] fail_to_pass
def test_parse_workflow_run_id_exists():
    """parseWorkflowRunId function must exist in the model and handle /actions/runs/ URLs."""
    src = Path(MODEL).read_text()
    assert "parseWorkflowRunId" in src, "parseWorkflowRunId function not found in model"
    assert "/actions/runs/" in src, "Function must handle /actions/runs/{id} URL pattern"


# [pr_diff] fail_to_pass
def test_parse_workflow_run_id_behavior():
    """parseWorkflowRunId must correctly extract run IDs from diverse GitHub Actions URLs."""
    # Behavioral: test the required parsing spec via Node.js with diverse URL inputs.
    # AST-only because: TypeScript source cannot be directly require()'d without compilation
    script = r"""
const cases = [
    ['https://github.com/owner/repo/actions/runs/12345/job/6789', 12345],
    ['https://github.com/owner/repo/actions/runs/99999', 99999],
    ['https://github.com/owner/repo/actions/runs/1', 1],
    ['https://github.com/foo/bar/actions/runs/5557890123', 5557890123],
    ['https://github.com/owner/repo/checks/run/123', undefined],
    [undefined, undefined],
    ['', undefined],
    ['https://example.com/no/match', undefined],
];
// Extract the parseWorkflowRunId function from the source file
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
// Find the function body — it should be a standalone function
const fnMatch = src.match(/function\s+parseWorkflowRunId\s*\([^)]*\)\s*(?::\s*[^{]+)?\{/);
if (!fnMatch) { console.error('parseWorkflowRunId function not found in source'); process.exit(1); }
const fnStart = fnMatch.index;
// Find matching closing brace
let depth = 0, fnEnd = -1;
for (let i = fnStart; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) { fnEnd = i + 1; break; } }
}
if (fnEnd < 0) { console.error('Could not find end of parseWorkflowRunId'); process.exit(1); }
const fnSrc = src.slice(fnStart, fnEnd)
    .replace(/:\s*string\s*\|\s*undefined/g, '')
    .replace(/:\s*number\s*\|\s*undefined/g, '')
    .replace(/:\s*string/g, '')
    .replace(/:\s*number/g, '');
eval(fnSrc);
let ok = true;
for (const [url, expected] of cases) {
    const got = parseWorkflowRunId(url);
    if (got !== expected) {
        console.error('FAIL: parseWorkflowRunId(' + JSON.stringify(url) + ') = ' + JSON.stringify(got) + ', expected ' + JSON.stringify(expected));
        ok = false;
    }
}
process.exit(ok ? 0 : 1);
""" % MODEL
    r = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, "Regex spec test failed:\n" + r.stderr + r.stdout


# [pr_diff] fail_to_pass
def test_rerun_button_shown_for_failed_checks():
    """ciStatusWidget must add a rerun action button only for Failed check groups."""
    src = Path(WIDGET).read_text()
    assert "ci.rerunCheck" in src, "ci.rerunCheck action ID missing from widget"
    assert "CICheckGroup.Failed" in src, "Rerun action must be gated on CICheckGroup.Failed"
    assert "rerunFailedCheck" in src, "Widget must call model.rerunFailedCheck()"


# [pr_diff] fail_to_pass
def test_rerun_api_uses_post():
    """The rerunFailedJobs method must use POST for the GitHub Actions API call."""
    src = Path(FETCHER).read_text()
    # Find the rerunFailedJobs method and verify it uses POST
    method_match = re.search(r'async rerunFailedJobs.*?\n(.*?)\n\s*\}', src, re.DOTALL)
    assert method_match, "rerunFailedJobs method not found"
    body = method_match.group(1)
    assert "'POST'" in body or '"POST"' in body, "rerunFailedJobs must use POST method"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_ci_methods_preserved():
    """Existing CI fetcher and model methods must not be removed by the change."""
    fetcher_src = Path(FETCHER).read_text()
    model_src = Path(MODEL).read_text()
    assert "getCheckRuns" in fetcher_src, "getCheckRuns must remain in fetcher"
    assert "getCheckRunAnnotations" in model_src, "getCheckRunAnnotations must remain in model"


# [repo_tests] pass_to_pass
def test_existing_widget_open_on_github_preserved():
    """The existing 'Open on GitHub' action must not be removed from the widget."""
    src = Path(WIDGET).read_text()
    assert "ci.openOnGitHub" in src, "ci.openOnGitHub action must remain in widget"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:136 @ 64e73b036669494bbc9a6904cf090b01a8d3bb1e
def test_named_regex_capture_groups():
    """Regex in parseWorkflowRunId must use named capture groups, not numbered ones."""
    # .github/copilot-instructions.md line 136:
    # "Prefer regex capture groups with names over numbered capture groups."
    src = Path(MODEL).read_text()
    assert "(?<" in src, "Must use named regex capture groups like (?<runId>...) per copilot-instructions.md:136"
    # Verify the named group is actually used via .groups accessor
    assert ".groups" in src, "Must access named groups via match.groups"
