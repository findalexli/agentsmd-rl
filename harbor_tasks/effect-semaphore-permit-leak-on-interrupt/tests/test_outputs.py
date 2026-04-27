"""Behavioral tests for PR Effect-TS/effect#6081 — semaphore permit leak fix."""
import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")
EFFECT_PKG = REPO / "packages" / "effect"
LEAK_TEST = EFFECT_PKG / "test" / "Effect" / "leak_regression.test.ts"


def _vitest(test_path: str, timeout: int = 240) -> subprocess.CompletedProcess:
    """Run vitest from packages/effect for a single test file."""
    return subprocess.run(
        ["pnpm", "exec", "vitest", "run", "--no-coverage", test_path],
        cwd=str(EFFECT_PKG),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# --- f2p: behavioural fix --------------------------------------------------

def test_take_interruption_does_not_leak_permits():
    """Interrupting a fiber that is waiting for a permit must not consume the permit.

    fail_to_pass: at base, the observer claims the permit before the waiting
    fiber resumes; if the fiber is then interrupted, the claimed permit is
    never released, leaving the semaphore at zero free permits.
    """
    assert LEAK_TEST.exists(), f"regression test file missing: {LEAK_TEST}"
    r = _vitest("test/Effect/leak_regression.test.ts", timeout=180)
    assert r.returncode == 0, (
        "leak_regression.test.ts failed — semaphore permits are leaking on interrupt.\n"
        f"--- stdout (last 2000 chars) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (last 1000 chars) ---\n{r.stderr[-1000:]}"
    )
    # Sanity: vitest must have actually picked up and run the test file.
    assert "test/Effect/leak_regression.test.ts" in r.stdout, (
        "vitest output does not show the regression test file ran"
    )
    assert "1 passed" in r.stdout, (
        f"vitest did not report 1 passed test for the regression file:\n{r.stdout[-1000:]}"
    )


# --- p2p: regression coverage from upstream tests --------------------------

def test_existing_semaphore_tests_still_pass():
    """The semaphore.test.ts suite that already shipped at base must still pass.

    pass_to_pass: the fix must not break `semaphore works`, `releaseAll`, `resize`.
    """
    r = _vitest("test/Effect/semaphore.test.ts", timeout=240)
    assert r.returncode == 0, (
        f"upstream semaphore.test.ts regressed.\n"
        f"--- stdout (last 2000 chars) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (last 1000 chars) ---\n{r.stderr[-1000:]}"
    )


def test_typecheck_effect_src():
    """The effect package must still type-check after the fix.

    pass_to_pass: catches half-baked TS edits that break the project's type build.
    """
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit", "-p", "tsconfig.src.json"],
        cwd=str(EFFECT_PKG),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"tsc -p tsconfig.src.json failed:\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-1000:]}"
    )
