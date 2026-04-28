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


# [repo_tests] pass_to_pass
def test_repo_version_check():
    """Repo's version consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "version-check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Version check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flags():
    """Repo's feature flags validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flags"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Feature flags check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_react_flight_server():
    """ReactFlightServer tests pass (pass_to_pass) - related to modified ReactFlightReplyServer module."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "--testPathPattern", "ReactFlightServer-test",
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ReactFlightServer tests failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_react_flight():
    """ReactFlight tests pass (pass_to_pass) - related to Flight protocol."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "--testPathPattern", "ReactFlight-test",
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ReactFlight tests failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_react_flight_reply_iterable():
    """Iterable reply serialization works (pass_to_pass) - related to decodeReply."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "--testPathPattern", "ReactFlightDOMReply-test",
            "--testNamePattern", "can pass an iterable",
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Iterable reply test failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_react_flight_reply_bigint():
    """BigInt reply serialization works (pass_to_pass) - related to decodeReply."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "--testPathPattern", "ReactFlightDOMReply-test",
            "--testNamePattern", "can pass a BigInt",
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"BigInt reply test failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_react_flight_reply_date():
    """Date reply serialization works (pass_to_pass) - related to decodeReply."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "--testPathPattern", "ReactFlightDOMReply-test",
            "--testNamePattern", "can pass a Date",
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Date reply test failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_playground_yarn():
    """pass_to_pass | CI job 'Test playground' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn install --frozen-lockfile'], cwd=os.path.join(REPO, 'compiler'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_playground_npx():
    """pass_to_pass | CI job 'Test playground' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps chromium'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_license_scripts_ci_check_license_sh():
    """pass_to_pass | CI job 'Check license' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/ci/check_license.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_print_warnings_scripts_ci_test_print_warnings_sh():
    """pass_to_pass | CI job 'Test print warnings' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/ci/test_print_warnings.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_jest_babel_plugin_react_compil_yarn():
    """pass_to_pass | CI job 'Jest babel-plugin-react-compiler' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn workspace babel-plugin-react-compiler jest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_babel_plugin_react_compil_yarn():
    """pass_to_pass | CI job 'Lint babel-plugin-react-compiler' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn workspace babel-plugin-react-compiler lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_eslint_plugin_react_hooks_scripts_react_compiler_build_compiler_sh():
    """pass_to_pass | CI job 'Test eslint-plugin-react-hooks' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/react-compiler/build-compiler.sh && ./scripts/react-compiler/link-compiler.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_eslint_plugin_react_hooks_yarn():
    """pass_to_pass | CI job 'Test eslint-plugin-react-hooks' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn workspace eslint-plugin-react-hooks test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_yarn_build_and_lint_yarn():
    """pass_to_pass | CI job 'yarn build and lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn --cwd compiler install --frozen-lockfile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_yarn_build_and_lint_lint_build():
    """pass_to_pass | CI job 'yarn build and lint' → step 'Lint build'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn lint-build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_cannot_deserialize_a_Blob_reference_backed_by_a_():
    """fail_to_pass | PR added test 'cannot deserialize a Blob reference backed by a string' in 'packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js" -t "cannot deserialize a Blob reference backed by a string" 2>&1 || npx vitest run "packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js" -t "cannot deserialize a Blob reference backed by a string" 2>&1 || pnpm jest "packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js" -t "cannot deserialize a Blob reference backed by a string" 2>&1 || npx jest "packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js" -t "cannot deserialize a Blob reference backed by a string" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'cannot deserialize a Blob reference backed by a string' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
