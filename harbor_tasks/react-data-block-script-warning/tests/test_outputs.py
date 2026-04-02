"""
Task: react-data-block-script-warning
Repo: facebook/react @ 4cc5b7a90bac7e1f8ac51a9ac570d3ada3bddcb3
PR:   35953

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The fix adds isScriptDataBlock() to ReactFiberConfigDOM.js and gates the
trusted-types script warning so it is NOT emitted for data block scripts
(non-JS MIME types like application/json, application/ld+json).
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
CONFIG_FILE = f"{REPO}/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """ReactFiberConfigDOM.js must parse without JavaScript syntax errors."""
    r = subprocess.run(
        ["node", "--check", CONFIG_FILE],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Syntax error in {CONFIG_FILE}:\n"
        f"{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_isscriptdatablock_defined():
    """isScriptDataBlock function must be defined in ReactFiberConfigDOM.js."""
    content = Path(CONFIG_FILE).read_text()
    assert "function isScriptDataBlock" in content, (
        "isScriptDataBlock function not found in ReactFiberConfigDOM.js; "
        "the fix has not been applied"
    )


# [pr_diff] fail_to_pass
def test_warning_guarded_by_isscriptdatablock():
    """The trusted-types script warning must be gated on !isScriptDataBlock(props)."""
    content = Path(CONFIG_FILE).read_text()
    assert "!isScriptDataBlock" in content, (
        "Warning is not guarded by !isScriptDataBlock(props); "
        "data block scripts will incorrectly trigger the warning"
    )


# [pr_diff] fail_to_pass
def test_js_mime_types_excluded_from_data_block():
    """isScriptDataBlock must treat standard JavaScript MIME types as non-data-blocks.

    The function must enumerate known JS MIME types so they return false
    (i.e. are treated as executable scripts, not data blocks).
    Checks several required entries from the mimesniff spec list.
    """
    content = Path(CONFIG_FILE).read_text()
    # These must all appear inside isScriptDataBlock (the switch cases)
    required_js_mime_types = [
        "text/javascript",
        "application/javascript",
        "application/ecmascript",
        "text/ecmascript",
    ]
    for mime in required_js_mime_types:
        assert mime in content, (
            f"JS MIME type '{mime}' not found in isScriptDataBlock; "
            "the function must exclude standard JS MIME types from data-block classification"
        )


# [pr_diff] fail_to_pass
def test_special_keywords_not_data_blocks():
    """isScriptDataBlock must return false for HTML spec special keywords.

    'module', 'importmap', and 'speculationrules' are executable script types
    per the HTML spec — they must NOT be treated as data blocks.
    """
    content = Path(CONFIG_FILE).read_text()
    for keyword in ("module", "importmap", "speculationrules"):
        assert keyword in content, (
            f"Keyword '{keyword}' not found in isScriptDataBlock; "
            "the function must explicitly handle HTML spec special keywords"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_warning_test_passes():
    """The pre-existing Jest test 'should warn when rendering script tag' must still pass.

    An untyped <script> (no type attribute) must still trigger the trusted-types
    warning — the fix must not suppress all warnings.
    """
    r = subprocess.run(
        [
            "yarn",
            "test",
            "--silent",
            "--no-watchman",
            "-t",
            "should warn when rendering script tag",
            "trustedTypes-test.internal",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    stdout = r.stdout.decode()
    stderr = r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing 'should warn' Jest test failed (regression):\n"
        f"stdout: {stdout[-2000:]}\nstderr: {stderr[-1000:]}"
    )
    # Confirm the test actually ran (not just "no tests found")
    assert "Tests:" in stdout or "passed" in stdout or "✓" in stdout or "✗" in stdout, (
        f"No test results found — test may not have run:\n{stdout[-1000:]}"
    )
