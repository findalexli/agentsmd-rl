"""
Task: react-flight-blob-type-validation
Repo: facebook/react @ c80a07509582daadf275f36ffe7a88c3b12e9db4
PR:   36055

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified ReactFlightReplyServer.js must parse without errors."""
    r = subprocess.run(
        ["node", "--check", "packages/react-server/src/ReactFlightReplyServer.js"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in ReactFlightReplyServer.js:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_blob_validation_rejects_string():
    """String-backed $B reference must throw 'Referenced Blob is not a Blob.'"""
    # On base commit: new test case doesn't exist → Jest finds 0 tests → exit nonzero.
    # On fix: new test exists and the error is thrown → Jest exits 0 with PASS.
    r = subprocess.run(
        [
            "node", "--experimental-vm-modules", "node_modules/.bin/jest",
            "packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js",
            "--testNamePattern=cannot deserialize a Blob reference backed by a string",
            "--silent", "--no-watchman", "--testTimeout=30000",
        ],
        cwd=REPO, capture_output=True, timeout=180,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0 and "PASS" in output, (
        f"Jest test 'cannot deserialize a Blob reference backed by a string' did not pass:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_instanceof_blob_check_in_source():
    """ReactFlightReplyServer.js must validate backing entry with instanceof Blob."""
    src = Path(f"{REPO}/packages/react-server/src/ReactFlightReplyServer.js").read_text()
    assert "instanceof Blob" in src, (
        "Missing `instanceof Blob` type check in ReactFlightReplyServer.js — "
        "the fix must guard the $B deserialization path"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_blob_deserialization_works():
    """Valid Blob references must still serialize and deserialize correctly."""
    r = subprocess.run(
        [
            "node", "--experimental-vm-modules", "node_modules/.bin/jest",
            "packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js",
            "--testNamePattern=can serialize and deserialize a Blob",
            "--silent", "--no-watchman", "--testTimeout=30000",
        ],
        cwd=REPO, capture_output=True, timeout=180,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0 and "PASS" in output, (
        f"Existing Blob serialization/deserialization test broken:\n{output}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rule from .claude/skills/extract-errors/SKILL.md:8
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/extract-errors/SKILL.md:8 @ c80a07509582daadf275f36ffe7a88c3b12e9db4
def test_error_code_582_registered():
    """New error 'Referenced Blob is not a Blob.' must be registered in codes.json.

    Rule: 'Run yarn extract-errors when adding new error messages'
    (.claude/skills/extract-errors/SKILL.md:8)
    """
    codes_path = Path(f"{REPO}/scripts/error-codes/codes.json")
    codes = json.loads(codes_path.read_text())
    assert "582" in codes, (
        "Error code 582 not registered in scripts/error-codes/codes.json — "
        "new error messages must be extracted via yarn extract-errors"
    )
    assert "Blob" in codes["582"], (
        f"Error code 582 message doesn't mention Blob: {codes['582']!r}"
    )
