import subprocess
import shutil
import os

REPO = "/workspace/effect"
TESTS_DIR = "/tests"

SEMAPHORE_RACE_TEST_2 = """\
import { assert, describe, it } from "@effect/vitest"
import * as Effect from "effect/Effect"
import * as FiberId from "effect/FiberId"
import * as Option from "effect/Option"
import * as Scheduler from "effect/Scheduler"

describe("Semaphore Race", () => {
  it.effect("take(2) interruption does not leak permits", () =>
    Effect.gen(function*() {
      const scheduler = new Scheduler.ControlledScheduler()
      const sem = yield* Effect.makeSemaphore(0)
      const waiter = yield* sem.take(2).pipe(
        Effect.withScheduler(scheduler),
        Effect.fork
      )

      yield* Effect.yieldNow()
      yield* sem.release(2).pipe(Effect.withScheduler(scheduler))
      assert.isNull(waiter.unsafePoll())

      scheduler.step()
      assert.isNull(waiter.unsafePoll())

      waiter.unsafeInterruptAsFork(FiberId.none)
      scheduler.step()

      const result = yield* sem.withPermitsIfAvailable(2)(Effect.void)
      assert.isTrue(Option.isSome(result))
    }))
})
"""


def test_semaphore_race_leak():
    """Semaphore.take() must not leak permits when a waiter is interrupted."""
    dst = os.path.join(REPO, "packages/effect/test/Effect/semaphore_race.test.ts")
    shutil.copy(os.path.join(TESTS_DIR, "semaphore_race_test.ts"), dst)

    r = subprocess.run(
        ["pnpm", "test", "packages/effect/test/Effect/semaphore_race.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Semaphore race test failed (returncode={r.returncode}):\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )


def test_semaphore_race_leak_2():
    """Semaphore.take(2) must not leak permits when a waiter is interrupted."""
    dst = os.path.join(REPO, "packages/effect/test/Effect/semaphore_race_2.test.ts")
    with open(dst, "w") as f:
        f.write(SEMAPHORE_RACE_TEST_2)

    r = subprocess.run(
        ["pnpm", "test", "packages/effect/test/Effect/semaphore_race_2.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Semaphore race test 2 failed (returncode={r.returncode}):\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )


def test_existing_semaphore_tests():
    """Existing semaphore tests continue to pass."""
    r = subprocess.run(
        ["pnpm", "test", "packages/effect/test/Effect/semaphore.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Existing semaphore tests failed (returncode={r.returncode}):\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
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