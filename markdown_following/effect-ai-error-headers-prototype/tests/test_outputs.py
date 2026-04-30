"""Behavioral tests for effect-ts/effect#6101.

The bug: AiError.HttpRequestError / AiError.HttpResponseError run schema
validation in their constructors, which strips the prototype off
@effect/platform Headers objects, losing the Redactable behavior. The fix
disables that validation so the original Headers prototype is preserved.

Tests run vitest inside the cloned monorepo against a TS test that
constructs the AiError types from platform HttpClientError values and
asserts Headers.isHeaders(...) on the resulting fields.
"""

import json
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")
AI_PKG = REPO / "packages/ai/ai"
TEST_DIR = AI_PKG / "test"
SRC_TEST = Path("/tests/AiError.headers.test.ts")
DEST_TEST = TEST_DIR / "AiError.headers.test.ts"


def _ensure_test_file_in_place():
    """Copy our headers test into the package's test/ directory."""
    DEST_TEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC_TEST, DEST_TEST)


def _run_vitest(test_filter: str) -> subprocess.CompletedProcess:
    _ensure_test_file_in_place()
    return subprocess.run(
        ["pnpm", "exec", "vitest", "run", "--reporter=json", "--", test_filter],
        cwd=str(AI_PKG),
        capture_output=True,
        text=True,
        timeout=300,
    )


def _vitest_results(test_filter: str) -> dict:
    proc = _run_vitest(test_filter)
    stdout = proc.stdout
    start = stdout.find("{")
    end = stdout.rfind("}")
    assert start != -1 and end != -1, (
        f"vitest produced no JSON.\nstdout:\n{stdout[-2000:]}\nstderr:\n{proc.stderr[-2000:]}"
    )
    return json.loads(stdout[start : end + 1])


def _find_test_result(results: dict, name_substring: str) -> dict:
    for tf in results.get("testResults", []):
        for assertion in tf.get("assertionResults", []):
            full = assertion.get("fullName", "") or assertion.get("title", "")
            if name_substring in full:
                return assertion
    raise AssertionError(
        f"Could not find a test matching {name_substring!r} in vitest output. "
        f"Saw: {[a.get('fullName') for tf in results.get('testResults', []) for a in tf.get('assertionResults', [])]}"
    )


# ---- fail-to-pass: behavior tests ----------------------------------------

def test_request_error_preserves_headers_prototype():
    """fromRequestError result must keep Headers prototype on .request.headers."""
    results = _vitest_results("test/AiError.headers.test.ts")
    res = _find_test_result(results, "preserves the Headers prototype on the request")
    assert res["status"] == "passed", (
        f"Expected pass, got {res['status']}. "
        f"Failure messages: {res.get('failureMessages')}"
    )


def test_response_error_preserves_request_headers_prototype():
    """fromResponseError must keep Headers prototype on .request.headers."""
    results = _vitest_results("test/AiError.headers.test.ts")
    matches = []
    for tf in results.get("testResults", []):
        for a in tf.get("assertionResults", []):
            full = a.get("fullName", "") or a.get("title", "")
            if "HttpResponseError" in full and "request" in full and "preserves the Headers prototype" in full:
                matches.append(a)
    assert matches, "Did not find HttpResponseError request-headers test"
    for a in matches:
        assert a["status"] == "passed", (
            f"Expected pass, got {a['status']}. Failure: {a.get('failureMessages')}"
        )


def test_response_error_preserves_response_headers_prototype():
    """fromResponseError must keep Headers prototype on .response.headers."""
    results = _vitest_results("test/AiError.headers.test.ts")
    matches = []
    for tf in results.get("testResults", []):
        for a in tf.get("assertionResults", []):
            full = a.get("fullName", "") or a.get("title", "")
            if "HttpResponseError" in full and "response" in full and "preserves the Headers prototype" in full:
                matches.append(a)
    assert matches, "Did not find HttpResponseError response-headers test"
    for a in matches:
        assert a["status"] == "passed", (
            f"Expected pass, got {a['status']}. Failure: {a.get('failureMessages')}"
        )


# ---- pass-to-pass: existing repo CI tests --------------------------------

def test_repo_ai_existing_tests():
    """All pre-existing @effect/ai vitest suites still pass."""
    proc = subprocess.run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "test/Chat.test.ts",
            "test/LanguageModel.test.ts",
            "test/Prompt.test.ts",
            "test/Tool.test.ts",
        ],
        cwd=str(AI_PKG),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, (
        f"Existing @effect/ai tests failed.\nstdout:\n{proc.stdout[-2000:]}\n"
        f"stderr:\n{proc.stderr[-2000:]}"
    )


def test_repo_ai_typecheck():
    """The @effect/ai package still type-checks."""
    proc = subprocess.run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.json"],
        cwd=str(AI_PKG),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode == 0, (
        f"Type check failed.\nstdout:\n{proc.stdout[-2000:]}\n"
        f"stderr:\n{proc.stderr[-2000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_pnpm():
    """pass_to_pass | CI job 'Build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docgen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm circular'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_2():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_3():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm codegen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_for_codegen_changes():
    """pass_to_pass | CI job 'Lint' → step 'Check for codegen changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'git diff --exit-code'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for codegen changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")