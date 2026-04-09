"""
Task: react-action-state-error-message
Repo: react @ 3bc2d414287e62a7b74731c6c7b837270353a339
PR:   35790

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"

HOOKS_FILE = "packages/react-reconciler/src/ReactFiberHooks.js"
CODES_FILE = "scripts/error-codes/codes.json"
TEST_FILE = "packages/react-dom/src/__tests__/ReactDOMForm-test.js"

EXPECTED_MSG = "Cannot update action state while rendering."


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_codes_json_valid():
    """error-codes/codes.json must be valid JSON with error code 485."""
    codes_path = Path(REPO) / CODES_FILE
    content = codes_path.read_text()
    data = json.loads(content)
    assert isinstance(data, dict), "codes.json root must be an object"
    assert "485" in data, "Error code 485 must exist in codes.json"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_error_message_in_hooks():
    """dispatchActionState must throw 'Cannot update action state while rendering.'"""
    src = Path(REPO, HOOKS_FILE).read_text()

    # Find the dispatchActionState function and its error message
    match = re.search(
        r"function\s+dispatchActionState[\s\S]*?throw\s+new\s+Error\(\s*['\"]([^'\"]+)['\"]\s*\)",
        src,
    )
    assert match is not None, (
        "Could not find throw statement in dispatchActionState function"
    )
    actual_msg = match.group(1)
    assert actual_msg == EXPECTED_MSG, (
        f"Error message mismatch: got {actual_msg!r}, expected {EXPECTED_MSG!r}"
    )


# [pr_diff] fail_to_pass
def test_error_code_485():
    """Error code 485 in codes.json must say 'action state' — verified via Node."""
    # Use Node subprocess to parse and validate the JSON (behavioral test for JS repo)
    script = (
        "const d = JSON.parse(require('fs').readFileSync("
        "'scripts/error-codes/codes.json', 'utf8'));"
        "const msg = d['485'];"
        "const expected = 'Cannot update action state while rendering.';"
        "if (msg !== expected) {"
        "  process.stderr.write('Expected: ' + expected + '\\nGot: ' + msg);"
        "  process.exit(1);"
        "}"
        "process.stdout.write(msg);"
    )
    r = subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, timeout=10,
    )
    assert r.returncode == 0, (
        f"Error code 485 mismatch:\n{r.stderr.decode()}"
    )
    assert r.stdout.decode() == EXPECTED_MSG


# [pr_diff] fail_to_pass
def test_test_expects_action_state():
    """The ReactDOMForm test must await waitForThrow with 'action state'."""
    test_src = Path(REPO, TEST_FILE).read_text()

    # Find all waitForThrow calls that mention "state while rendering"
    matches = re.findall(
        r"waitForThrow\(\s*['\"]([^'\"]*state while rendering[^'\"]*)['\"]",
        test_src,
    )
    assert len(matches) > 0, (
        "Could not find waitForThrow call about state while rendering"
    )
    for m in matches:
        assert "action state" in m, (
            f"Test still references old wording: {m!r}"
        )
        assert "form state" not in m, (
            f"Test still uses old 'form state' wording: {m!r}"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .claude/skills/extract-errors
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/extract-errors/SKILL.md:10-12
def test_error_codes_in_sync():
    """Error code 485 in codes.json must match the throw message in source.

    From .claude/skills/extract-errors/SKILL.md: 'Check if error codes are up to date'
    """
    # Extract error message from source
    src = Path(REPO, HOOKS_FILE).read_text()
    match = re.search(
        r"function\s+dispatchActionState[\s\S]*?throw\s+new\s+Error\(\s*['\"]([^'\"]+)['\"]\s*\)",
        src,
    )
    assert match is not None, "Could not find error in dispatchActionState"
    source_msg = match.group(1)

    # Extract error code 485 from codes.json
    data = json.loads(Path(REPO, CODES_FILE).read_text())
    code_msg = data["485"]

    # They must match (extract-errors skill: error codes must be up to date)
    assert source_msg == code_msg, (
        f"Error code 485 out of sync with source.\n"
        f"  Source: {source_msg!r}\n"
        f"  codes.json: {code_msg!r}"
    )

    # Both must reference "action state" (the current API name)
    assert "action state" in source_msg, (
        f"Source error uses wrong terminology: {source_msg!r}"
    )
