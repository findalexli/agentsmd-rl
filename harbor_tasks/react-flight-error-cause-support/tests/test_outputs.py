"""
Task: react-flight-error-cause-support
Repo: facebook/react @ 38cd020c1fb8a1e88b7852160796f411926a6fac
PR:   35810

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_can_transport_error_cause():
    """Error.cause property is serialized by server and revived on the client."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "packages/react-client/src/__tests__/ReactFlight-test.js",
            "-t", "can transport Error\\.cause",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Test 'can transport Error.cause' failed:\n{output}"


# [pr_diff] fail_to_pass
def test_error_cause_in_thrown_errors():
    """Error.cause is preserved when a Server Component throws."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "packages/react-client/src/__tests__/ReactFlight-test.js",
            "-t", "includes Error\\.cause in thrown errors",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Test 'includes Error.cause in thrown errors' failed:\n{output}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural (type system changes)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: Flow type definitions cannot be executed
def test_jsonvalue_exported_from_shared():
    """JSONValue type is consolidated and exported from packages/shared/ReactTypes.js."""
    content = Path(f"{REPO}/packages/shared/ReactTypes.js").read_text()
    assert "export type JSONValue" in content, (
        "JSONValue type must be exported from packages/shared/ReactTypes.js "
        "(it was previously duplicated in client and server files)"
    )


# [pr_diff] fail_to_pass
# AST-only because: Flow type definitions cannot be executed
def test_cause_field_in_error_info_type():
    """ReactErrorInfoDev type in ReactTypes.js includes an optional cause field."""
    content = Path(f"{REPO}/packages/shared/ReactTypes.js").read_text()
    # The field `cause?: JSONValue` must appear inside ReactErrorInfoDev
    assert "cause?" in content, (
        "ReactErrorInfoDev in packages/shared/ReactTypes.js must declare "
        "an optional `cause?` field to carry the error cause chain"
    )


# [pr_diff] fail_to_pass
# AST-only because: Flow type definitions cannot be executed
def test_jsonvalue_not_locally_defined_in_client():
    """JSONValue local definition is removed from ReactFlightClient.js (now imported from shared)."""
    content = Path(f"{REPO}/packages/react-client/src/ReactFlightClient.js").read_text()
    assert "export type JSONValue" not in content, (
        "JSONValue should no longer be locally defined in ReactFlightClient.js; "
        "it should be imported from packages/shared/ReactTypes.js"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_flight_cyclic_transport():
    """Pre-existing ReactFlight cyclic-object test still passes (no regression)."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "packages/react-client/src/__tests__/ReactFlight-test.js",
            "-t", "can transport cyclic objects",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Regression in existing ReactFlight test:\n{output}"


# [repo_tests] pass_to_pass
def test_flight_error_objects():
    """ReactFlight Error object transport test passes (no regression in Error serialization)."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "packages/react-client/src/__tests__/ReactFlight-test.js",
            "-t", "can transport Error objects as values",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Error object transport test failed:\n{output}"


# [repo_tests] pass_to_pass
def test_flight_replays_logs_cyclic():
    """ReactFlight cyclic object logging test passes (no regression)."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "packages/react-client/src/__tests__/ReactFlight-test.js",
            "-t", "replays logs with cyclic objects",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Cyclic logs test failed:\n{output}"


# [repo_tests] pass_to_pass
def test_flight_formdata():
    """ReactFlight FormData transport test passes (no regression)."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "packages/react-client/src/__tests__/ReactFlight-test.js",
            "-t", "can transport FormData",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"FormData transport test failed:\n{output}"
