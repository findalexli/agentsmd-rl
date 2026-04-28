"""Pytest harness that drives vitest + the repo's lint/typecheck.

Each `def test_*` function maps 1:1 to a check id in eval_manifest.yaml.

f2p tests (1-3) exercise the gold-patch behaviour: they fail at the base
commit and pass on the gold patch.

p2p tests (4-5) come from the repo's own CI: they pass at the base commit
and must continue passing on the gold patch.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/excalidraw")
CUSTOM_TEST = "packages/element/tests/__oob_fix__.test.tsx"


def _ensure_custom_test_present() -> None:
    """Copy the custom vitest test into the repo if test.sh hasn't already."""
    src = Path("/tests/oob_fix.test.tsx")
    dst = REPO / CUSTOM_TEST
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists() and (not dst.exists() or src.read_bytes() != dst.read_bytes()):
        shutil.copy2(src, dst)


def _run_vitest(test_name_pattern: str, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a single vitest case from the custom test file by `-t` name pattern."""
    _ensure_custom_test_present()
    cmd = [
        "yarn",
        "test:app",
        "run",
        CUSTOM_TEST,
        "-t",
        test_name_pattern,
    ]
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _vitest_passed(result: subprocess.CompletedProcess, test_substring: str) -> None:
    """Assert that vitest reports a pass for a test whose name contains the substring.

    Defensive checks:
      1. exit code == 0
      2. the test name appears in the output (vitest's `-t` filter matched it)
      3. at least one test actually passed (guards against silent no-match)
      4. the failure marker (×) does NOT appear next to the test name
    """
    output = result.stdout + "\n" + result.stderr
    assert result.returncode == 0, (
        f"vitest exited {result.returncode}.\n"
        f"--- last 1500 chars of stdout ---\n{result.stdout[-1500:]}\n"
        f"--- last 800 chars of stderr ---\n{result.stderr[-800:]}\n"
    )
    assert test_substring in output, (
        f"expected vitest output to mention '{test_substring}' (the -t filter "
        f"matched no test); got:\n{output[-1500:]}"
    )
    # vitest summary line: "Tests  N passed | M skipped (T)". Require N >= 1.
    import re

    summary = re.search(r"Tests\s+(\d+)\s+passed", output)
    assert summary, (
        f"could not find 'Tests N passed' summary in vitest output:\n"
        f"{output[-1500:]}"
    )
    assert int(summary.group(1)) >= 1, (
        f"vitest reported 0 passed tests; full output:\n{output[-1500:]}"
    )
    # No failure marker for our specific test name.
    fail_line = any(
        ("×" in line or "FAIL" in line) and test_substring in line
        for line in output.splitlines()
    )
    assert not fail_line, (
        f"vitest reported a failure for '{test_substring}':\n{output[-1500:]}"
    )


# ---------------------------------------------------------------------------
# f2p — fail on the base commit, pass on the gold patch
# ---------------------------------------------------------------------------

def test_handle_point_dragging_oob_index():
    """handlePointDragging must not throw when lastClickedPoint is out of range.

    On the base commit, an `invariant(...)` call throws on the corrupted state
    reported in Sentry. The gold patch replaces it with a `console.error` and a
    fallback to `element.points.length - 1`.
    """
    name = "tolerates an out-of-range lastClickedPoint without throwing"
    result = _run_vitest(name)
    _vitest_passed(result, name)


def test_handle_point_dragging_negative_index():
    """handlePointDragging must not throw when lastClickedPoint is negative."""
    name = "tolerates a negative lastClickedPoint without throwing"
    result = _run_vitest(name)
    _vitest_passed(result, name)


def test_repair_binding_diagnostic_format():
    """restoreElements must log the new diagnostic format including the
    candidate elements-map size when a binding cannot be repaired.

    Old log: ``could not repair binding for element``
    New log: ``Could not repair binding for element "<id>" out of (N) elements``
    """
    name = "logs the new diagnostic format when binding cannot be repaired"
    result = _run_vitest(name)
    _vitest_passed(result, name)


# ---------------------------------------------------------------------------
# p2p — pass on the base commit, must keep passing on the gold patch
# ---------------------------------------------------------------------------

def test_repo_typecheck():
    """`yarn test:typecheck` (tsc) must succeed on the gold patch."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"yarn test:typecheck failed.\nstdout tail:\n{result.stdout[-1500:]}\n"
        f"stderr tail:\n{result.stderr[-800:]}"
    )


def test_repo_existing_linear_element_editor_tests():
    """The repo's own linearElementEditor.test.tsx suite must keep passing.

    This is a strong p2p signal: the gold patch touches the same file these
    tests exercise.
    """
    result = subprocess.run(
        [
            "yarn",
            "test:app",
            "run",
            "packages/element/tests/linearElementEditor.test.tsx",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"vitest on linearElementEditor.test.tsx failed.\n"
        f"stdout tail:\n{result.stdout[-1500:]}\n"
        f"stderr tail:\n{result.stderr[-800:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_install_and_test():
    """pass_to_pass | CI job 'test' → step 'Install and test'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn install && yarn test:app'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Install and test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")