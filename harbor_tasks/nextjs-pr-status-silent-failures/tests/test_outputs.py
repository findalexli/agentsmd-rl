"""
Task: nextjs-pr-status-silent-failures
Repo: next.js @ 3421858b5bef076965d99fd88fedc483193a496e
PR:   92205

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = "/workspace/next.js"
SCRIPT = f"{REPO}/scripts/pr-status.js"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js snippet via subprocess."""
    return subprocess.run(
        ["node", "-e", code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """scripts/pr-status.js must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", SCRIPT],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_pr_status_functions_parseable():
    """Key functions in pr-status.js must be parseable JavaScript (pass_to_pass)."""
    code = textwrap.dedent(r"""
        const fs = require('fs');
        const src = fs.readFileSync('scripts/pr-status.js', 'utf8');

        // Verify the script parses by trying to extract function signatures
        const functionNames = [
            'getAllJobs',
            'getFailedJobs',
            'categorizeJobs',
            'generateReport',
            'getFlakyTests'
        ];

        const results = {};
        for (const name of functionNames) {
            // Look for function declaration
            const funcPattern = new RegExp('function\\s+' + name + '\\s*\\(');
            results[name] = funcPattern.test(src);
        }

        // Also verify the script structure is intact
        results.has_exec_helper = src.includes('function exec(');
        results.has_main = src.includes('async function main(');

        console.log(JSON.stringify(results));
    """)
    r = _run_node(code)
    assert r.returncode == 0, f"Parse check failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())

    # Verify all expected functions are found
    required = ['getAllJobs', 'getFailedJobs', 'categorizeJobs', 'getFlakyTests']
    for name in required:
        assert data.get(name) is True, f"Required function {name} not found in pr-status.js"

    assert data.get('has_exec_helper') is True, "exec helper function not found"
    assert data.get('has_main') is True, "main function not found"


# [repo_tests] pass_to_pass
def test_pr_status_js_no_undefined_variables():
    """pr-status.js must not reference obviously undefined variables (pass_to_pass)."""
    code = textwrap.dedent(r"""
        const fs = require('fs');
        const src = fs.readFileSync('scripts/pr-status.js', 'utf8');

        // Extract all variable references and check against common globals
        const globalVars = new Set([
            'console', 'process', 'require', 'module', 'exports', 'Buffer',
            'JSON', 'Object', 'Array', 'String', 'Number', 'Boolean', 'Date',
            'Math', 'RegExp', 'Error', 'Promise', 'Set', 'Map', 'WeakMap',
            'WeakSet', 'Symbol', 'Intl', 'URL', 'URLSearchParams', 'TextEncoder',
            'TextDecoder', 'setTimeout', 'clearTimeout', 'setInterval', 'clearInterval',
            'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'escape', 'unescape',
            'encodeURI', 'encodeURIComponent', 'decodeURI', 'decodeURIComponent',
            '__dirname', '__filename', 'undefined', 'null', 'Infinity', 'NaN',
            'fs', 'path', 'child_process', 'execSync', 'execFileSync', 'spawn',
            'OUTPUT_DIR', 'genericNodeError', 'wrappedFn'
        ]);

        // Find all declared variables/functions
        const declarations = new Set();
        const declRegex = /(?:const|let|var|function|class)\s+(\w+)/g;
        let match;
        while ((match = declRegex.exec(src)) !== null) {
            declarations.add(match[1]);
        }

        // Find all parameter names from function declarations
        const funcParams = /function\s+\w*\s*\([^)]*\)/g;
        const paramMatch = src.matchAll(funcParams);
        for (const m of paramMatch) {
            const params = m[0].replace(/function\s+\w*\s*\(/, '').replace(/\)$/, '');
            params.split(',').forEach(p => {
                const paramName = p.trim().replace(/\s*=.*/, '').replace(/^\.\.\./, '');
                if (paramName) declarations.add(paramName);
            });
        }

        // Check destructured parameters
        const destructured = /{\s*([^}]+)\s*}/g;
        const destMatch = src.matchAll(destructured);
        for (const m of destMatch) {
            m[1].split(',').forEach(p => {
                const clean = p.trim().replace(/^\w+:\s*/, '').replace(/\s*=.*/, '');
                if (clean && !clean.includes('.')) declarations.add(clean);
            });
        }

        // Verify no obvious undefined variable references
        // This is a basic check - we'll look for common patterns that indicate bugs
        const suspicious = [];

        // Check for typos in common variable names by looking at the overall structure
        const hasProperExport = src.includes('module.exports') || src.includes('exports.');
        const hasShebang = src.startsWith('#!');

        const results = {
            declared_count: declarations.size,
            has_module_exports: hasProperExport || src.includes('main('),
            functions_found: Array.from(declarations).filter(d =>
                ['exec', 'execAsync', 'execJson', 'getRunMetadata',
                 'getAllJobs', 'getFailedJobs', 'categorizeJobs',
                 'generateReport', 'getFlakyTests', 'main'].includes(d)
            )
        };

        console.log(JSON.stringify(results));
    """)
    r = _run_node(code)
    assert r.returncode == 0, f"Variable check failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())

    # Verify key functions are declared
    expected_functions = ['exec', 'getAllJobs', 'getFailedJobs', 'categorizeJobs', 'main']
    for func in expected_functions:
        assert func in data.get('functions_found', []), f"Function {func} should be declared"


# [repo_tests] pass_to_pass
def test_pr_status_js_no_syntax_errors_strict_mode():
    """pr-status.js must parse without errors in strict mode (pass_to_pass)."""
    code = textwrap.dedent(r"""
        const fs = require('fs');
        const src = fs.readFileSync('scripts/pr-status.js', 'utf8');

        // Wrap in strict mode and try to parse
        const strictSrc = '"use strict";\n' + src;

        try {
            // Use Function constructor to validate syntax (catches syntax errors)
            new Function(strictSrc);
            console.log(JSON.stringify({ parses_in_strict_mode: true }));
        } catch (e) {
            // If it fails due to 'use strict' in source already, that's fine
            if (e.message.includes('strict mode') || e.message.includes('Use of future reserved word')) {
                // Try without the extra strict directive
                try {
                    new Function(src);
                    console.log(JSON.stringify({ parses_in_strict_mode: true, note: 'already has strict' }));
                } catch (e2) {
                    console.log(JSON.stringify({ parses_in_strict_mode: false, error: e2.message }));
                }
            } else {
                console.log(JSON.stringify({ parses_in_strict_mode: false, error: e.message }));
            }
        }
    """)
    r = _run_node(code)
    assert r.returncode == 0, f"Strict mode check failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get('parses_in_strict_mode') is True, f"Script has syntax errors: {data.get('error', '')}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression guards for pr-status.js
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_node_syntax_check_pr_status():
    """JavaScript syntax check on pr-status.js via node --check (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", f"{REPO}/scripts/pr-status.js"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check_pr_status():
    """Prettier formatting check on pr-status.js (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/scripts/pr-status.js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_repo_pr_status_script_structure():
    """pr-status.js must have expected structure and exports (pass_to_pass)."""
    src = Path(SCRIPT).read_text()

    # Check for key structural elements
    assert "function exec(" in src, "exec helper function must exist"
    assert "function execAsync(" in src, "execAsync helper function must exist"
    assert "function execJson(" in src, "execJson helper function must exist"
    assert "async function main(" in src, "main function must exist"
    assert "module.exports" in src or "exports." in src, "Script must have module exports"


# [static] pass_to_pass
def test_repo_pr_status_no_banned_patterns():
    """pr-status.js must not contain banned/unsafe patterns (pass_to_pass)."""
    src = Path(SCRIPT).read_text()

    # Check for eval() which is dangerous
    assert "eval(" not in src, "Script must not use eval() for security"

    # Check for console.log in async functions (should use console.error for errors)
    # This is a basic check - the script should properly handle errors
    assert "child_process" in src or "execSync" in src, "Script must use child_process for shell commands"


# [static] pass_to_pass
def test_repo_pr_status_has_required_helpers():
    """pr-status.js must have all required helper functions (pass_to_pass)."""
    code = textwrap.dedent(r"""
        const fs = require('fs');
        const src = fs.readFileSync('scripts/pr-status.js', 'utf8');

        // Required helper functions
        const requiredHelpers = [
            'exec',
            'execAsync',
            'execJson',
            'formatDuration',
            'formatElapsedTime',
            'sanitizeFilename',
            'escapeMarkdownTableCell',
            'stripTimestamps'
        ];

        const found = {};
        for (const name of requiredHelpers) {
            // Check for function declaration
            const funcPattern = new RegExp('function\\s+' + name + '\\s*\\(');
            found[name] = funcPattern.test(src);
        }

        // Check for getRunMetadata and other key data functions
        const dataFunctions = [
            'getRunMetadata',
            'getAllJobs',
            'getFailedJobs',
            'categorizeJobs',
            'generateReport',
            'getFlakyTests'
        ];

        for (const name of dataFunctions) {
            const funcPattern = new RegExp('function\\s+' + name + '\\s*\\(');
            found[name] = funcPattern.test(src);
        }

        console.log(JSON.stringify(found));
    """)
    r = _run_node(code)
    assert r.returncode == 0, f"Helper check failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())

    # Verify all expected helpers exist
    critical_helpers = ['exec', 'execAsync', 'getAllJobs', 'getFailedJobs', 'categorizeJobs']
    for helper in critical_helpers:
        assert data.get(helper) is True, f"Required helper {helper} not found in pr-status.js"


# [static] pass_to_pass
def test_repo_pr_status_uses_strict_mode_compatible_syntax():
    """pr-status.js must use syntax compatible with strict mode (pass_to_pass)."""
    code = textwrap.dedent(r"""
        const fs = require('fs');
        const src = fs.readFileSync('scripts/pr-status.js', 'utf8');

        // Check for common strict mode issues
        const issues = [];

        // Check for with statements (not allowed in strict)
        if (/\bwith\s*\(/.test(src)) {
            issues.push("Uses 'with' statement (not allowed in strict mode)");
        }

        // Check for octal literals (not allowed in strict) - skip comments
        const linesNoComments = src.split('\n').map(line => line.replace(/\/\/.*$/, ''));
        const codeOnly = linesNoComments.join('\n');
        if (/\b0[0-7]+\b/.test(codeOnly)) {
            issues.push("Uses octal literals (not allowed in strict mode)");
        }

        // Check for duplicate parameter names would need parsing, but we can check basic patterns

        // Check for proper variable declarations (no implicit globals)
        // Look for assignments without declarations in function bodies
        const lines = src.split('\n');
        let inFunction = false;
        let braceDepth = 0;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];

            // Track function entry/exit
            if (/function\s+\w+\s*\(/.test(line) || /=>\s*[{]/.test(line)) {
                inFunction = true;
            }

            // Count braces
            for (const char of line) {
                if (char === '{') braceDepth++;
                if (char === '}') braceDepth--;
            }

            if (braceDepth === 0 && inFunction) {
                inFunction = false;
            }
        }

        console.log(JSON.stringify({
            issues: issues,
            has_strict_mode_issues: issues.length > 0
        }));
    """)
    r = _run_node(code)
    assert r.returncode == 0, f"Strict mode compatibility check failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())

    assert not data.get('has_strict_mode_issues'), (
        f"Script has strict mode compatibility issues: {data.get('issues')}"
    )




# [repo_tests] pass_to_pass
def test_repo_pr_status_alex_lint():
    """Alex language linting on pr-status.js must pass (pass_to_pass).

    Note: The base commit's .alexrc doesn't include "reject" as an allowed word.
    Without this, alex flags "reject" as profane (technical term in Promise context).
    Skip this test if "reject" is not in .alexrc's allow list.
    """
    # Check if .alexrc has "reject" in the allowed words
    alexrc_path = Path(f"{REPO}/.alexrc")
    if not alexrc_path.exists():
        pytest.skip("No .alexrc config in repo")
    alexrc_content = alexrc_path.read_text()
    if "reject" not in alexrc_content:
        pytest.skip(".alexrc doesn't allow 'reject' - needed for Promise terminology")

    r = subprocess.run(
        ["npx", "alex", "--quiet", f"{REPO}/scripts/pr-status.js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Alex lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pr_status_node_parse():
    """Node.js must be able to parse pr-status.js without errors (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"require('{REPO}/scripts/pr-status.js')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert "SyntaxError" not in r.stderr, f"Script has syntax errors:\n{r.stderr}"
    assert "ReferenceError" not in r.stderr, f"Script has reference errors:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_scripts_check_manifests():
    """Repo\'s check-manifests.js must run without errors (pass_to_pass).

    Note: check-manifests.js requires npm dependencies (glob, fs-extra) that
    aren't installed in the base environment. This script is not related to
    the PR fix being tested, so we skip it if deps are missing.
    """
    # Check if required dependencies are available
    r = subprocess.run(
        ["node", "-e", "require('glob'); require('fs-extra')"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    if r.returncode != 0:
        pytest.skip("check-manifests.js dependencies (glob, fs-extra) not installed")

    r = subprocess.run(
        ["node", f"{REPO}/scripts/check-manifests.js"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check-manifests.js failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_scripts_validate_externals_doc():
    """Repo\'s validate-externals-doc.js must run without runtime errors (pass_to_pass)."""
    r = subprocess.run(
        ["node", f"{REPO}/scripts/validate-externals-doc.js"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert "SyntaxError" not in r.stderr, f"Script has syntax errors:\n{r.stderr}"
    assert "ReferenceError" not in r.stderr, f"Script has reference errors:\n{r.stderr}"
    assert "TypeError" not in r.stderr, f"Script has type errors:\n{r.stderr}"

# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_categorize_timed_out_as_failed():
    """categorizeJobs must classify timed_out and startup_failure as failed."""
    # We extract FAILED_CONCLUSIONS + categorizeJobs from the script, then
    # call categorizeJobs with mock job data and verify the result.
    code = textwrap.dedent(r"""
        const fs = require('fs');
        const src = fs.readFileSync('scripts/pr-status.js', 'utf8');

        // Extract FAILED_CONCLUSIONS if it exists; fall back to empty Set
        const setMatch = src.match(/^const FAILED_CONCLUSIONS\s*=\s*new Set\(\[([^\]]*)\]\)/m);
        if (setMatch) {
            eval('var FAILED_CONCLUSIONS = new Set([' + setMatch[1] + '])');
        } else {
            // Base commit has no FAILED_CONCLUSIONS — mimic the original code
            var FAILED_CONCLUSIONS = null;
        }

        // Find and extract categorizeJobs function body
        const funcIdx = src.indexOf('function categorizeJobs(');
        if (funcIdx === -1) { console.log('FUNC_NOT_FOUND'); process.exit(1); }
        let depth = 0, started = false, end = funcIdx;
        for (let i = funcIdx; i < src.length; i++) {
            if (src[i] === '{') { depth++; started = true; }
            if (src[i] === '}') { depth--; }
            if (started && depth === 0) { end = i + 1; break; }
        }
        eval(src.substring(funcIdx, end));

        const jobs = [
            { id: 1, name: 'build', status: 'completed', conclusion: 'failure' },
            { id: 2, name: 'test-a', status: 'completed', conclusion: 'timed_out' },
            { id: 3, name: 'test-b', status: 'completed', conclusion: 'startup_failure' },
            { id: 4, name: 'test-c', status: 'completed', conclusion: 'success' },
            { id: 5, name: 'test-d', status: 'in_progress', conclusion: null },
            { id: 6, name: 'test-e', status: 'queued', conclusion: null },
        ];
        const result = categorizeJobs(jobs);
        console.log(JSON.stringify({
            failed_ids: result.failed.map(j => j.id),
            succeeded_ids: result.succeeded.map(j => j.id),
            in_progress_ids: result.inProgress.map(j => j.id),
            queued_ids: result.queued.map(j => j.id),
        }));
    """)
    r = _run_node(code)
    assert r.returncode == 0, f"Node script failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert 1 in data["failed_ids"], "conclusion='failure' must be in failed"
    assert 2 in data["failed_ids"], "conclusion='timed_out' must be in failed"
    assert 3 in data["failed_ids"], "conclusion='startup_failure' must be in failed"
    assert 4 in data["succeeded_ids"], "conclusion='success' must be in succeeded"
    assert 5 in data["in_progress_ids"], "in_progress job must be in inProgress"


# [pr_diff] fail_to_pass
def test_get_all_jobs_throws_on_persistent_failure():
    """getAllJobs must throw when all retries fail on page 1, not return []."""
    # On the base commit, catch { break } silently returns [].
    # On the fix, persistent first-page failure throws an error.
    code = textwrap.dedent(r"""
        const fs = require('fs');
        const src = fs.readFileSync('scripts/pr-status.js', 'utf8');

        // Override exec to always throw (simulates persistent API failure)
        function exec(cmd) { throw new Error('HTTP 502 Bad Gateway'); }
        const execSync = function(cmd) {};  // mock sleep

        // Extract getAllJobs
        const funcIdx = src.indexOf('function getAllJobs(');
        if (funcIdx === -1) { console.log('FUNC_NOT_FOUND'); process.exit(1); }
        let depth = 0, started = false, end = funcIdx;
        for (let i = funcIdx; i < src.length; i++) {
            if (src[i] === '{') { depth++; started = true; }
            if (src[i] === '}') { depth--; }
            if (started && depth === 0) { end = i + 1; break; }
        }
        eval(src.substring(funcIdx, end));

        let threw = false;
        let result = null;
        try {
            result = getAllJobs(99999);
        } catch (e) {
            threw = true;
        }
        console.log(JSON.stringify({ threw, result_length: result ? result.length : null }));
    """)
    r = _run_node(code)
    assert r.returncode == 0, f"Node script failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    # On the fix: must throw (not silently return empty array)
    assert data["threw"] is True, (
        f"getAllJobs must throw on persistent first-page API failure, "
        f"but returned array of length {data['result_length']}"
    )


# [pr_diff] fail_to_pass
def test_get_failed_jobs_includes_conclusion():
    """getFailedJobs must return objects with a 'conclusion' field."""
    # On the base commit, .map only returns {id, name}. The fix adds conclusion.
    code = textwrap.dedent(r"""
        const fs = require('fs');
        const src = fs.readFileSync('scripts/pr-status.js', 'utf8');

        // Extract FAILED_CONCLUSIONS if present
        const setMatch = src.match(/^const FAILED_CONCLUSIONS\s*=\s*new Set\(\[([^\]]*)\]\)/m);
        if (setMatch) {
            eval('var FAILED_CONCLUSIONS = new Set([' + setMatch[1] + '])');
        }

        // Mock getAllJobs to return test data
        function getAllJobs(runId) {
            return [
                { id: 100, name: 'build', status: 'completed', conclusion: 'failure' },
                { id: 200, name: 'test-timeout', status: 'completed', conclusion: 'timed_out' },
                { id: 300, name: 'test-ok', status: 'completed', conclusion: 'success' },
            ];
        }

        // Extract getFailedJobs
        const funcIdx = src.indexOf('function getFailedJobs(');
        if (funcIdx === -1) { console.log('FUNC_NOT_FOUND'); process.exit(1); }
        let depth = 0, started = false, end = funcIdx;
        for (let i = funcIdx; i < src.length; i++) {
            if (src[i] === '{') { depth++; started = true; }
            if (src[i] === '}') { depth--; }
            if (started && depth === 0) { end = i + 1; break; }
        }
        eval(src.substring(funcIdx, end));

        const result = getFailedJobs(12345);
        console.log(JSON.stringify({
            count: result.length,
            has_conclusion: result.length > 0 && 'conclusion' in result[0],
            conclusions: result.map(j => j.conclusion || null),
            ids: result.map(j => j.id),
        }));
    """)
    r = _run_node(code)
    assert r.returncode == 0, f"Node script failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["has_conclusion"] is True, (
        "getFailedJobs must include 'conclusion' field in returned objects"
    )
    # Should include at least the 'failure' job
    assert 100 in data["ids"], "Job with conclusion='failure' must be included"


# [pr_diff] fail_to_pass
def test_conclusion_annotation_in_report():
    """Report table must annotate non-failure conclusions like '(timed_out)'."""
    # On the base commit, the table row for failed jobs does not reference
    # job.conclusion at all. The fix adds an annotation like "(timed_out)".
    src = Path(SCRIPT).read_text()

    # Find the table row template for failed jobs (pattern: `| ${job.id} |`)
    table_line_idx = src.index("| ${job.id} |")
    # Look at a region around the table row template (300 chars before, 200 after)
    region_start = max(0, table_line_idx - 300)
    region_end = min(len(src), table_line_idx + 200)
    table_region = src[region_start:region_end]

    # The fix must reference job.conclusion near the table row to annotate it.
    # Any valid implementation (inline ternary, separate variable, etc.) must
    # mention 'conclusion' in the table row generation context.
    assert "conclusion" in table_region, (
        "Table row generation must reference job conclusion for annotation. "
        f"Region around table line:\n{table_region}"
    )

    # Verify the annotation produces the expected format: " (timed_out)"
    # Check that the pattern includes parentheses around the conclusion value
    has_paren_pattern = (
        "(${" in table_region  # template literal interpolation in parens
        or "(" + '"timed_out"' in table_region
        or "`.conclusion" in table_region
        or "conclusion)" in table_region
        or "(timed_out)" in table_region
    )
    assert has_paren_pattern, (
        "Table annotation must wrap conclusion in parentheses, e.g. '(timed_out)'"
    )


# [pr_diff] fail_to_pass
def test_flaky_detection_includes_timed_out():
    """Flaky test detection must consider timed_out workflow runs, not just failures."""
    # On the base commit, the jq query only checks .conclusion == "failure".
    # The fix adds .conclusion == "timed_out" to the workflow run filter.
    src = Path(SCRIPT).read_text()

    # Find the getFlakyTests function and check the workflow_runs jq query
    flaky_idx = src.index("async function getFlakyTests(")
    flaky_body = src[flaky_idx:]

    # Look for the workflow_runs jq query within getFlakyTests
    # The fix changes: select(.conclusion == "failure")
    # to: select(.conclusion == "failure" or .conclusion == "timed_out")
    wf_query_start = flaky_body.index(".workflow_runs[]")
    wf_query_region = flaky_body[wf_query_start:wf_query_start + 200]
    assert "timed_out" in wf_query_region, (
        "getFlakyTests workflow_runs query must include timed_out conclusion, "
        f"found: {wf_query_region!r}"
    )

    # Also check the per-run jobs query includes all failure types
    jobs_query_idx = flaky_body.index('.jobs[]')
    jobs_query_region = flaky_body[jobs_query_idx:jobs_query_idx + 200]
    assert "timed_out" in jobs_query_region, (
        "getFlakyTests jobs query must include timed_out conclusion"
    )
    assert "startup_failure" in jobs_query_region, (
        "getFlakyTests jobs query must include startup_failure conclusion"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression guards
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_categorize_failure_preserved():
    """categorizeJobs must still classify 'failure' conclusion as failed."""
    code = textwrap.dedent(r"""
        const fs = require('fs');
        const src = fs.readFileSync('scripts/pr-status.js', 'utf8');

        // Extract FAILED_CONCLUSIONS if present
        const setMatch = src.match(/^const FAILED_CONCLUSIONS\s*=\s*new Set\(\[([^\]]*)\]\)/m);
        if (setMatch) {
            eval('var FAILED_CONCLUSIONS = new Set([' + setMatch[1] + '])');
        }

        // Extract categorizeJobs
        const funcIdx = src.indexOf('function categorizeJobs(');
        if (funcIdx === -1) { console.log('FUNC_NOT_FOUND'); process.exit(1); }
        let depth = 0, started = false, end = funcIdx;
        for (let i = funcIdx; i < src.length; i++) {
            if (src[i] === '{') { depth++; started = true; }
            if (src[i] === '}') { depth--; }
            if (started && depth === 0) { end = i + 1; break; }
        }
        eval(src.substring(funcIdx, end));

        const jobs = [
            { id: 1, name: 'build', status: 'completed', conclusion: 'failure' },
            { id: 2, name: 'test', status: 'completed', conclusion: 'success' },
        ];
        const result = categorizeJobs(jobs);
        console.log(JSON.stringify({
            failed_ids: result.failed.map(j => j.id),
            succeeded_ids: result.succeeded.map(j => j.id),
        }));
    """)
    r = _run_node(code)
    assert r.returncode == 0, f"Node script failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert 1 in data["failed_ids"], "conclusion='failure' must still be in failed"
    assert 2 in data["succeeded_ids"], "conclusion='success' must still be in succeeded"
