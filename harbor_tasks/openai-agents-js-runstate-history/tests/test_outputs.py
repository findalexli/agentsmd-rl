"""Behavioural tests for the openai-agents-js RunState.history task.

Each test_* function corresponds 1:1 with a check id in eval_manifest.yaml.
The TS oracle (check_history.ts) is invoked via tsx; its line-prefixed
output (`CHECK <name>: PASS|FAIL ...`) is parsed to attribute results
to individual python tests.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/openai-agents-js")
PKG = REPO / "packages" / "agents-core"
TSX_BIN = REPO / "node_modules" / ".bin" / "tsx"

ORACLE_TS_SRC = Path("/tests/check_history.ts")
ORACLE_TS_DST = PKG / "check_history_oracle.ts"


@pytest.fixture(scope="module")
def oracle_output() -> dict[str, str]:
    """Run the oracle script once and parse its output.

    Returns a mapping from check name to the full status line (`PASS`
    or `FAIL <reason>`).
    """
    shutil.copyfile(ORACLE_TS_SRC, ORACLE_TS_DST)
    try:
        env = os.environ.copy()
        env["NODE_ENV"] = "test"
        result = subprocess.run(
            [str(TSX_BIN), str(ORACLE_TS_DST.name)],
            cwd=PKG,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    finally:
        if ORACLE_TS_DST.exists():
            ORACLE_TS_DST.unlink()

    combined = result.stdout + result.stderr
    parsed: dict[str, str] = {}
    for line in combined.splitlines():
        line = line.strip()
        if not line.startswith("CHECK "):
            continue
        rest = line[len("CHECK ") :]
        try:
            name, status = rest.split(": ", 1)
        except ValueError:
            continue
        parsed[name] = status

    parsed["__returncode__"] = str(result.returncode)
    parsed["__raw__"] = combined
    return parsed


def _assert_check(parsed: dict[str, str], check_name: str) -> None:
    raw = parsed.get("__raw__", "")
    status = parsed.get(check_name)
    assert status is not None, (
        f"Oracle check '{check_name}' did not appear in tsx output. "
        f"This usually means the script crashed before reaching it.\n"
        f"--- oracle output (last 2000 chars) ---\n{raw[-2000:]}"
    )
    assert status.startswith("PASS"), (
        f"Oracle check '{check_name}' failed: {status}\n"
        f"--- oracle output (last 2000 chars) ---\n{raw[-2000:]}"
    )


# ---------------------------------------------------------------------------
# fail_to_pass: behavioural oracle (4 distinct assertions)
# ---------------------------------------------------------------------------


def test_history_string_input_with_generated_item(oracle_output: dict[str, str]) -> None:
    """history = [{user-message-from-string}, ...generatedItems.rawItem]."""
    _assert_check(oracle_output, "string_input_with_generated_item")


def test_history_string_input_no_generated_items(oracle_output: dict[str, str]) -> None:
    """With no generated items, history wraps the string input only."""
    _assert_check(oracle_output, "string_input_no_generated_items")


def test_history_array_input_preserves_order(oracle_output: dict[str, str]) -> None:
    """When _originalInput is an array, those items appear unchanged at the start."""
    _assert_check(oracle_output, "array_input_preserves_order")


def test_history_preserved_after_serialization(oracle_output: dict[str, str]) -> None:
    """history equals after a toString()/fromString() round-trip."""
    _assert_check(oracle_output, "preserved_after_serialization")


# ---------------------------------------------------------------------------
# pass_to_pass: build-check + lint
# ---------------------------------------------------------------------------


def test_agents_core_build_check() -> None:
    """`pnpm -F @openai/agents-core run build-check` must succeed.

    This compiles the package (and its test files) with `tsc --noEmit`,
    catching any TypeScript errors introduced by the change.
    """
    result = subprocess.run(
        ["pnpm", "-F", "@openai/agents-core", "run", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        "build-check failed.\n"
        f"--- stdout (last 2000 chars) ---\n{result.stdout[-2000:]}\n"
        f"--- stderr (last 2000 chars) ---\n{result.stderr[-2000:]}"
    )


def test_repo_lint() -> None:
    """`pnpm lint` must pass on the modified source tree."""
    result = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        "Lint failed.\n"
        f"--- stdout (last 2000 chars) ---\n{result.stdout[-2000:]}\n"
        f"--- stderr (last 2000 chars) ---\n{result.stderr[-2000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")