"""
Task: react-data-block-script-warning
Repo: react @ 4cc5b7a90bac7e1f8ac51a9ac570d3ada3bddcb3
PR:   35953

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/react"
TARGET = os.path.join(
    REPO,
    "packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js",
)

# Node.js helper: extracts the data-block detection function from source,
# strips Flow type annotations, and runs it against provided test cases.
_NODE_EXTRACT_AND_TEST = r"""
const fs = require('fs');
const targetFile = process.argv[2];
const testCases = JSON.parse(process.argv[3]);
const src = fs.readFileSync(targetFile, 'utf8');

// Find a function that checks whether a script is a data block.
// Accept various naming conventions an agent might use.
const patterns = [
    /function\s+(\w*[Dd]ata[Bb]lock\w*)\s*\(/,
    /function\s+(\w*[Nn]on[Ee]xecut\w*)\s*\(/,
    /function\s+(\w*[Ss]cript[Tt]ype\w*)\s*\(/,
];

let funcName = null, startIdx = -1;
for (const pat of patterns) {
    const m = src.match(pat);
    if (m) { funcName = m[1]; startIdx = src.indexOf(m[0]); break; }
}

if (startIdx === -1) {
    process.stderr.write('No data block detection function found in source\n');
    process.exit(1);
}

// Count braces to find function boundary
let depth = 0, inFunc = false, endIdx = -1;
for (let i = startIdx; i < src.length; i++) {
    if (src[i] === '{') { depth++; inFunc = true; }
    if (src[i] === '}') { depth--; }
    if (inFunc && depth === 0) { endIdx = i + 1; break; }
}

let funcSrc = src.slice(startIdx, endIdx);
// Strip Flow type annotations: (param: Type) -> (param), ): RetType { -> ) {
funcSrc = funcSrc.replace(/\(([a-zA-Z_]\w*)\s*:\s*[A-Z]\w*\)/g, '($1)');
funcSrc = funcSrc.replace(/\)\s*:\s*\w+\s*\{/g, ') {');

eval(funcSrc);
const fn = eval(funcName);

let failed = false;
for (const [props, expected] of testCases) {
    const result = fn(props);
    if (result !== expected) {
        process.stderr.write(
            'FAIL: ' + JSON.stringify(props) +
            ' expected=' + expected + ' got=' + result + '\n'
        );
        failed = true;
    }
}
if (failed) process.exit(1);
"""


def _run_data_block_tests(test_cases):
    """Extract data-block detection function and test it via Node.js subprocess.

    test_cases: list of [props_dict, expected_bool]
    """
    cases_json = json.dumps(test_cases)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(_NODE_EXTRACT_AND_TEST)
        script_path = f.name
    try:
        return subprocess.run(
            ["node", script_path, TARGET, cases_json],
            capture_output=True,
            timeout=30,
        )
    finally:
        os.unlink(script_path)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_data_blocks_recognized():
    """Data block types (application/json, application/ld+json, text/csv) must be
    recognized as non-executable script types."""
    cases = [
        [{"type": "application/json"}, True],
        [{"type": "application/ld+json"}, True],
        [{"type": "text/csv"}, True],
        [{"type": "application/xml"}, True],
    ]
    r = _run_data_block_tests(cases)
    assert r.returncode == 0, (
        f"Data block types not recognized as non-executable:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_js_mimes_not_data_blocks():
    """JavaScript MIME types must NOT be classified as data blocks."""
    cases = [
        [{"type": "text/javascript"}, False],
        [{"type": "application/javascript"}, False],
        [{"type": "application/ecmascript"}, False],
        [{"type": "text/jscript"}, False],
        [{"type": "text/livescript"}, False],
    ]
    r = _run_data_block_tests(cases)
    assert r.returncode == 0, (
        f"JS MIME types wrongly classified as data blocks:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_empty_and_special_types_not_data_blocks():
    """Empty type, missing type, and HTML spec keywords must NOT be data blocks."""
    cases = [
        [{"type": ""}, False],
        [{}, False],
        [{"type": "module"}, False],
        [{"type": "importmap"}, False],
        [{"type": "speculationrules"}, False],
    ]
    r = _run_data_block_tests(cases)
    assert r.returncode == 0, (
        f"Empty/special types wrongly classified as data blocks:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_warning_condition_gates_data_blocks():
    """The trusted types script-tag warning must be gated to skip data block scripts."""
    src = Path(TARGET).read_text()

    # The warning about script tags must still exist
    assert "Encountered a script tag" in src, "Script tag warning text not found"

    # Find the ~800 chars before the warning to check the condition
    warning_idx = src.index("Encountered a script tag")
    nearby = src[max(0, warning_idx - 800) : warning_idx]

    # The condition must reference data-block/type-checking logic
    has_gate = any(
        kw in nearby
        for kw in [
            "DataBlock",
            "dataBlock",
            "data_block",
            "nonExecut",
            "NonExecut",
            "scriptType",
            "ScriptType",
        ]
    )
    assert has_gate, (
        "Warning condition does not gate on data block detection. "
        "The trusted types warning should skip data block scripts "
        "(e.g., type='application/json')."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_script_tag_warning():
    """Existing trusted types test for regular script tag warnings must still pass."""
    r = subprocess.run(
        [
            "yarn",
            "test",
            "--silent",
            "--no-watchman",
            "--testPathPattern",
            "trustedTypes-test",
            "--testNamePattern",
            "should warn once when rendering script tag",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing trusted types script-tag warning test failed:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow():
    """Repo's Flow typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "dom-browser"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
