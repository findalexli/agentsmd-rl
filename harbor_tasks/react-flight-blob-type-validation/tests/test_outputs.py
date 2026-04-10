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
import re

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
    """String-backed $B reference must throw 'Referenced Blob is not a Blob.'

    Runs the PR's Jest test via yarn test (React's proper test runner).
    On base commit: test doesn't exist → Jest finds no match → 0 tests run.
    On fix: test exists and the instanceof check throws → Jest PASS.
    """
    r = subprocess.run(
        [
            "yarn", "test", "--json", "--no-watchman",
            "--testPathPattern", "ReactFlightDOMReply-test",
            "--testNamePattern", "cannot deserialize a Blob reference backed by a string",
        ],
        cwd=REPO, capture_output=True, timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    # Parse Jest JSON output - the last line containing "numTotalTests" is the summary
    # Jest exits 0 even when no tests match, so we need to check test counts
    total_tests = 0
    # Look for the summary JSON at the end of output
    # Extract the last JSON object that has numTotalTests
    json_pattern = r'"numTotalTests":\s*(\d+)'
    matches = re.findall(json_pattern, r.stdout.decode())
    if matches:
        total_tests = max(int(m) for m in matches)
    # If no tests ran, the test doesn't exist yet (base commit)
    assert total_tests > 0, (
        f"Jest found no matching tests - test 'cannot deserialize a Blob reference backed by a string' "
        f"does not exist on base commit:\n{output[-2000:]}"
    )
    assert r.returncode == 0, (
        f"Jest test 'cannot deserialize a Blob reference backed by a string' did not pass:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_react_flight_reply_formdata():
    """FormData with Blob serialization works (pass_to_pass)."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "--testPathPattern", "ReactFlightDOMReply-test",
            "--testNamePattern", "can pass FormData as a reply",
        ],
        cwd=REPO, capture_output=True, timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"FormData serialization test broken:\n{output[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_react_flight_reply_all():
    """All ReactFlightDOMReply tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "--testPathPattern", "ReactFlightDOMReply-test",
        ],
        cwd=REPO, capture_output=True, timeout=300,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"ReactFlightDOMReply tests failed:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_flow():
    """Repo's Flow typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow-ci"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    # Flow might fail due to environment issues - skip if it's an infrastructure problem
    if "inlinedHostConfig shortName" in r.stderr or "inlinedHostConfig shortName" in r.stdout:
        print("WARNING: Flow check skipped due to infrastructure issue (inlinedHostConfig)")
        return
    assert r.returncode == 0, f"Flow typecheck failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .claude/skills/
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/extract-errors/SKILL.md:10 @ c80a07509582daadf275f36ffe7a88c3b12e9db4
def test_error_code_registered():
    """New error 'Referenced Blob is not a Blob.' must be registered in codes.json.

    Rule: 'Run yarn extract-errors when adding new error messages'
    (.claude/skills/extract-errors/SKILL.md:10)
    """
    codes_path = Path(f"{REPO}/scripts/error-codes/codes.json")
    codes = json.loads(codes_path.read_text())
    # Find the error message by content, not by hardcoded code number.
    # The agent must register the error via yarn extract-errors, which assigns
    # the next available code number.
    blob_error_codes = [
        code for code, msg in codes.items()
        if "Referenced Blob is not a Blob" in msg
    ]
    assert len(blob_error_codes) >= 1, (
        "Error message 'Referenced Blob is not a Blob.' not registered in "
        "scripts/error-codes/codes.json — run yarn extract-errors"
    )
