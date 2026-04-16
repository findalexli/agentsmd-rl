"""
Fail-to-pass tests for openai/openai-agents-js#1129:
getInputItems omits empty pending_safety_checks / acknowledged_safety_checks
on replayed computer_call / computer_call_result items.
"""

import subprocess
import os
import json

REPO = "/workspace/openai-agents-js"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_tsx(script: str, timeout: int = 120) -> tuple[int, str, str]:
    """Run TypeScript script via tsx; return (returncode, stdout, stderr)."""
    r = subprocess.run(
        ["node_modules/.bin/tsx", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "NODE_NO_WARNINGS": "1"},
    )
    return r.returncode, r.stdout, r.stderr


def get_input_item(items_js: str, index: int = 0) -> dict:
    """Call getInputItems via tsx and return the JSON of the item at given index."""
    script = f"""
import {{ getInputItems }} from './packages/agents-openai/src/openaiResponsesModel.ts';
const items = getInputItems({items_js});
console.log(JSON.stringify(items));
"""
    rc, stdout, stderr = run_tsx(script)
    if rc != 0:
        raise RuntimeError(f"getInputItems failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")
    result = json.loads(stdout.strip())
    # getInputItems returns an array; return the item at the given index
    if isinstance(result, list):
        return result[index]
    return result


# ---------------------------------------------------------------------------
# Fail-to-pass: pending_safety_checks omitted when empty
# ---------------------------------------------------------------------------

def test_pending_safety_checks_omitted_when_empty():
    """
    On base commit (buggy): rebuilt computer_call INCLUDES pending_safety_checks: [].
    After fix: pending_safety_checks key is absent when the array is empty.
    """
    item = get_input_item([
        {
            "type": "computer_call",
            "id": "test-call-1",
            "callId": "call-1",
            "action": {"type": "wait"},
            "status": "completed",
            "providerData": {
                "pending_safety_checks": [],
            },
        },
    ])

    # The bug: base commit always includes pending_safety_checks: []
    # Fix: key is absent when array is empty
    assert "pending_safety_checks" not in item, (
        f"pending_safety_checks should be omitted when empty, but got: {item}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass: acknowledged_safety_checks omitted when empty
# ---------------------------------------------------------------------------

def test_acknowledged_safety_checks_omitted_when_empty():
    """
    On base commit (buggy): rebuilt computer_call_result INCLUDES
    acknowledged_safety_checks: [].
    After fix: key is absent when the array is empty.
    """
    item = get_input_item([
        {
            "type": "computer_call_result",
            "id": "test-result-1",
            "callId": "call-1",
            "output": {"data": "https://example.com/screenshot.png"},
            "providerData": {
                "acknowledged_safety_checks": [],
            },
        },
    ])

    # The bug: base commit always includes acknowledged_safety_checks: []
    # Fix: key is absent when array is empty
    assert "acknowledged_safety_checks" not in item, (
        f"acknowledged_safety_checks should be omitted when empty, but got: {item}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: non-empty safety checks are preserved
# ---------------------------------------------------------------------------

def test_non_empty_pending_safety_checks_preserved():
    """
    Non-empty pending_safety_checks must still be included after the fix.
    """
    item = get_input_item([
        {
            "type": "computer_call",
            "id": "test-call-2",
            "callId": "call-2",
            "action": {"type": "wait"},
            "status": "completed",
            "providerData": {
                "pending_safety_checks": [{"id": "check-1", "details": "OK"}],
            },
        },
    ])

    assert "pending_safety_checks" in item, (
        f"pending_safety_checks should be present when non-empty, but got: {item}"
    )
    assert item["pending_safety_checks"] == [{"id": "check-1", "details": "OK"}]


# ---------------------------------------------------------------------------
# Pass-to-pass: non-empty acknowledged_safety_checks are preserved
# ---------------------------------------------------------------------------

def test_non_empty_acknowledged_safety_checks_preserved():
    """
    Non-empty acknowledged_safety_checks must still be included after the fix.
    """
    item = get_input_item([
        {
            "type": "computer_call_result",
            "id": "test-result-2",
            "callId": "call-2",
            "output": {"data": "https://example.com/screenshot.png"},
            "providerData": {
                "acknowledged_safety_checks": [{"id": "check-2", "result": "passed"}],
            },
        },
    ])

    assert "acknowledged_safety_checks" in item, (
        f"acknowledged_safety_checks should be present when non-empty, but got: {item}"
    )
    assert item["acknowledged_safety_checks"] == [{"id": "check-2", "result": "passed"}]


# ---------------------------------------------------------------------------
# Pass-to-pass: repo test suite (agents-openai package only)
# ---------------------------------------------------------------------------

def test_repo_test_suite():
    """Repo's own test suite passes (pass_to_pass)."""
    # Run vitest on agents-openai test files from the repo root
    r = subprocess.run(
        ["node_modules/.bin/vitest", "run", "packages/agents-openai/test/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NODE_ENV": "test"},
    )
    assert r.returncode == 0, f"Test suite failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass: lint
# ---------------------------------------------------------------------------

def test_repo_lint():
    """Repo's linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass: type check
# ---------------------------------------------------------------------------

def test_repo_build_check():
    """Repo's type-check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "-C", "packages/agents-openai", "run", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Type-check failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass: dist type check
# ---------------------------------------------------------------------------

def test_repo_dist_check():
    """Repo's dist type-check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "-C", "packages/agents-openai", "run", "dist:check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"dist:check failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass: targeted unit tests (most relevant to modified code)
# ---------------------------------------------------------------------------

def test_repo_targeted_unit_tests():
    """Repo's targeted tests for openaiResponsesModel pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "node_modules/.bin/vitest", "run",
            "packages/agents-openai/test/openaiResponsesModel.test.ts",
            "packages/agents-openai/test/openaiResponsesModel.helpers.test.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NODE_ENV": "test"},
    )
    assert r.returncode == 0, f"Targeted tests failed:\n{r.stderr[-1000:]}"
