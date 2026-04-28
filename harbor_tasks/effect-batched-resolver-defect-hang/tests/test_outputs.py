"""Behavior tests for the batched-resolver-defect fix.

f2p: a request consumer waiting on a `RequestResolver.makeBatched` whose
work-effect dies with a defect must observe a Failure exit, not hang.
We assert this by writing a vitest test into the effect package and
running vitest. The fiber's poll must yield `Some(Failure(...))` within
a small live-clock window.

p2p: a previously-passing repo test must still pass; types must still
compile (pnpm check on the effect package).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/effect")
EFFECT_PKG = REPO / "packages" / "effect"
DEFECT_TEST_REL = "test/Effect/query-defect.test.ts"
DEFECT_TEST_ABS = EFFECT_PKG / DEFECT_TEST_REL

# Canonical f2p test content. We always write this before running vitest so
# the test exists whether or not the agent created it.
DEFECT_TEST_SRC = textwrap.dedent('''\
    import { describe, it } from "@effect/vitest"
    import { assertTrue } from "@effect/vitest/utils"
    import * as Effect from "effect/Effect"
    import * as Exit from "effect/Exit"
    import * as Fiber from "effect/Fiber"
    import * as Request from "effect/Request"
    import * as RequestResolver from "effect/RequestResolver"

    class GetValue extends Request.TaggedClass("GetValue")<string, never, { readonly id: number }> {}

    describe("batched resolver defect (oracle)", () => {
      it.live("resolver defect should not hang single consumer", () =>
        Effect.gen(function*() {
          const resolver = RequestResolver.makeBatched((_requests: Array<GetValue>) => Effect.die("boom"))

          const fiber = yield* Effect.request(new GetValue({ id: 1 }), resolver).pipe(
            Effect.fork
          )

          yield* Effect.sleep("500 millis")
          const poll = yield* Fiber.poll(fiber)

          assertTrue(
            poll._tag === "Some",
            "Fiber should have completed - resolver defect must not leave consumers hanging"
          )

          if (poll._tag === "Some") {
            assertTrue(Exit.isFailure(poll.value))
          }
        }))

      it.live("resolver defect should not hang multiple consumers", () =>
        Effect.gen(function*() {
          const resolver = RequestResolver.makeBatched((_requests: Array<GetValue>) => Effect.die("boom"))

          const fiber = yield* Effect.forEach(
            [1, 2, 3],
            (id) => Effect.request(new GetValue({ id }), resolver),
            { batching: true, concurrency: "unbounded" }
          ).pipe(Effect.fork)

          yield* Effect.sleep("500 millis")
          const poll = yield* Fiber.poll(fiber)

          assertTrue(
            poll._tag === "Some",
            "Fiber should have completed - resolver defect must not leave consumers hanging"
          )

          if (poll._tag === "Some") {
            assertTrue(Exit.isFailure(poll.value))
          }
        }))
    })
''')


def _ensure_defect_test_present() -> None:
    DEFECT_TEST_ABS.parent.mkdir(parents=True, exist_ok=True)
    DEFECT_TEST_ABS.write_text(DEFECT_TEST_SRC)


def _run(cmd: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "true"},
    )


# ---------------------------------------------------------------------------
# fail-to-pass: oracle behavior tests
# ---------------------------------------------------------------------------

def test_resolver_defect_does_not_hang_single_consumer() -> None:
    """A `Effect.request` waiting on a defective batched resolver must not
    hang. After 500ms the fiber must be polled with Some(Failure(...))."""
    _ensure_defect_test_present()
    r = _run(
        ["pnpm", "-s", "test", "run", DEFECT_TEST_REL,
         "-t", "resolver defect should not hang single consumer"],
        cwd=EFFECT_PKG,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"vitest failed (exit={r.returncode}); "
        f"this indicates the consumer fiber hangs on resolver defect.\n"
        f"--- STDOUT (last 2000) ---\n{r.stdout[-2000:]}\n"
        f"--- STDERR (last 1000) ---\n{r.stderr[-1000:]}"
    )


def test_resolver_defect_does_not_hang_multiple_consumers() -> None:
    """Multiple concurrent batched requests must all be released when the
    shared resolver dies with a defect."""
    _ensure_defect_test_present()
    r = _run(
        ["pnpm", "-s", "test", "run", DEFECT_TEST_REL,
         "-t", "resolver defect should not hang multiple consumers"],
        cwd=EFFECT_PKG,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"vitest failed (exit={r.returncode}).\n"
        f"--- STDOUT (last 2000) ---\n{r.stdout[-2000:]}\n"
        f"--- STDERR (last 1000) ---\n{r.stderr[-1000:]}"
    )


# ---------------------------------------------------------------------------
# pass-to-pass: repo regression tests
# ---------------------------------------------------------------------------

def test_repo_query_repro_still_passes() -> None:
    """An existing repo test exercising the request/resolver path must still
    pass after the fix (no regressions in the cleanup-on-success path)."""
    r = _run(
        ["pnpm", "-s", "test", "run", "test/Effect/query-repro.test.ts"],
        cwd=EFFECT_PKG,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"query-repro regression:\n--- STDOUT ---\n{r.stdout[-2000:]}\n"
        f"--- STDERR ---\n{r.stderr[-1000:]}"
    )


def test_repo_query_test_still_passes() -> None:
    """The main query.test.ts file (covering the happy path of batched
    resolvers) must still pass after the fix."""
    r = _run(
        ["pnpm", "-s", "test", "run", "test/Effect/query.test.ts"],
        cwd=EFFECT_PKG,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"query.test.ts regression:\n--- STDOUT ---\n{r.stdout[-2000:]}\n"
        f"--- STDERR ---\n{r.stderr[-1000:]}"
    )


def test_effect_package_typechecks() -> None:
    """`pnpm check` on the effect package must succeed - the fix must not
    introduce type errors. (CI runs the equivalent in its `Types` job.)"""
    r = _run(
        ["pnpm", "-s", "check"],
        cwd=EFFECT_PKG,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"tsc -b failed:\n--- STDOUT ---\n{r.stdout[-2000:]}\n"
        f"--- STDERR ---\n{r.stderr[-1000:]}"
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

def test_ci_build_pnpm():
    """pass_to_pass | CI job 'Build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docgen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")