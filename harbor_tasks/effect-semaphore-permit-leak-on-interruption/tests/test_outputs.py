"""Tests for effect-ts/effect#6081 — semaphore permit-leak fix.

The PR fixes a race condition in `Semaphore.take` where, if a fiber waiting
for permits is granted them and then interrupted before consuming them, the
`taken` counter is incremented but the permits are never used — they are
leaked. The fix wraps the increment inside `core.suspend` so it only runs
when the resumed effect actually executes (interrupted fibers skip it).

f2p tests run a custom vitest spec that exercises the interruption-while-
resuming path with `Scheduler.ControlledScheduler`, so the leak is reliably
reproducible (no flakiness from real-time scheduling).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/effect")
PKG = REPO / "packages" / "effect"
TEST_DIR = PKG / "test" / "Effect"
LEAK_TS = TEST_DIR / "leak_check.test.ts"

LEAK_TS_SOURCE = '''import { assert, describe, it } from "@effect/vitest"
import * as Effect from "effect/Effect"
import * as FiberId from "effect/FiberId"
import * as Option from "effect/Option"
import * as Scheduler from "effect/Scheduler"

describe("SemaphoreLeakCheck", () => {
  it.effect("interrupted take after release does not leak permits", () =>
    Effect.gen(function*() {
      const scheduler = new Scheduler.ControlledScheduler()
      const sem = yield* Effect.makeSemaphore(0)
      const waiter = yield* sem.take(1).pipe(
        Effect.withScheduler(scheduler),
        Effect.fork
      )

      yield* Effect.yieldNow()
      yield* sem.release(1).pipe(Effect.withScheduler(scheduler))
      assert.isNull(waiter.unsafePoll())

      scheduler.step()
      assert.isNull(waiter.unsafePoll())

      waiter.unsafeInterruptAsFork(FiberId.none)
      scheduler.step()

      const result = yield* sem.withPermitsIfAvailable(1)(Effect.void)
      assert.isTrue(Option.isSome(result))
    }))

  it.effect("permits remain available after multiple interrupted takes", () =>
    Effect.gen(function*() {
      const scheduler = new Scheduler.ControlledScheduler()
      const sem = yield* Effect.makeSemaphore(0)

      const w1 = yield* sem.take(1).pipe(Effect.withScheduler(scheduler), Effect.fork)
      const w2 = yield* sem.take(1).pipe(Effect.withScheduler(scheduler), Effect.fork)

      yield* Effect.yieldNow()
      yield* sem.release(2).pipe(Effect.withScheduler(scheduler))

      w1.unsafeInterruptAsFork(FiberId.none)
      w2.unsafeInterruptAsFork(FiberId.none)
      scheduler.step()
      scheduler.step()

      const r1 = yield* sem.withPermitsIfAvailable(1)(Effect.void)
      assert.isTrue(Option.isSome(r1))
      const r2 = yield* sem.withPermitsIfAvailable(1)(Effect.void)
      assert.isTrue(Option.isSome(r2))
    }))
})
'''


def _ensure_leak_test_installed() -> None:
    """Materialise our custom TS test file inside the repo (idempotent)."""
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    if not LEAK_TS.exists() or LEAK_TS.read_text() != LEAK_TS_SOURCE:
        LEAK_TS.write_text(LEAK_TS_SOURCE)


def _run_vitest(test_file: str, name_filter: str | None = None, timeout: int = 600) -> subprocess.CompletedProcess:
    cmd = ["pnpm", "exec", "vitest", "run", test_file, "--reporter=verbose"]
    if name_filter:
        cmd.extend(["-t", name_filter])
    return subprocess.run(
        cmd,
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "true"},
    )


# ──────────────────────────── fail_to_pass ────────────────────────────────────

def test_interrupted_take_releases_permit_back():
    """f2p: a permit granted to a waiter that gets interrupted before consuming
    must remain available — verified via ControlledScheduler so the race is
    deterministic.
    """
    _ensure_leak_test_installed()
    r = _run_vitest(
        "test/Effect/leak_check.test.ts",
        name_filter="interrupted take after release does not leak permits",
        timeout=600,
    )
    out = (r.stdout or "") + (r.stderr or "")
    assert r.returncode == 0, (
        f"vitest leak_check returncode={r.returncode}\nLAST OUTPUT:\n{out[-2000:]}"
    )


def test_no_leak_under_multiple_interrupted_waiters():
    """f2p: multiple waiters interrupted after a release must not collectively
    leak permits. This catches partial fixes that only handle the single-waiter
    case.
    """
    _ensure_leak_test_installed()
    r = _run_vitest(
        "test/Effect/leak_check.test.ts",
        name_filter="permits remain available after multiple interrupted takes",
        timeout=600,
    )
    out = (r.stdout or "") + (r.stderr or "")
    assert r.returncode == 0, (
        f"vitest leak_check returncode={r.returncode}\nLAST OUTPUT:\n{out[-2000:]}"
    )


def test_circular_ts_take_uses_deferred_evaluation():
    """f2p: the fix must defer the `taken += n` increment so it runs as part
    of the resumed effect, not synchronously inside the observer/async
    callback. Verified by exercising the interruption race; if increment is
    eager, the f2p tests above leak permits.
    """
    src = (PKG / "src" / "internal" / "effect" / "circular.ts").read_text()
    take_start = src.index("readonly take = (n: number)")
    take_end = src.index("updateTakenUnsafe", take_start)
    take_body = src[take_start:take_end]
    suspend_uses = take_body.count("core.suspend") + take_body.count(".suspend(")
    assert suspend_uses >= 1, (
        "Semaphore.take should defer the taken increment via core.suspend so "
        f"interrupted fibers don't leak permits; found {suspend_uses} suspend calls"
    )


# ──────────────────────────── pass_to_pass ────────────────────────────────────

def test_existing_semaphore_works():
    """p2p: the original 'semaphore works' test still passes."""
    r = _run_vitest("test/Effect/semaphore.test.ts", name_filter="semaphore works", timeout=600)
    out = (r.stdout or "") + (r.stderr or "")
    assert r.returncode == 0, f"semaphore works failed:\n{out[-1500:]}"


def test_existing_semaphore_releaseall():
    """p2p: 'releaseAll' test still passes."""
    r = _run_vitest("test/Effect/semaphore.test.ts", name_filter="releaseAll", timeout=600)
    out = (r.stdout or "") + (r.stderr or "")
    assert r.returncode == 0, f"releaseAll failed:\n{out[-1500:]}"


def test_existing_semaphore_resize():
    """p2p: 'resize' test still passes (this exercises the same waiter path
    that's modified by the fix, so it's a good regression guard).
    """
    r = _run_vitest("test/Effect/semaphore.test.ts", name_filter="resize", timeout=600)
    out = (r.stdout or "") + (r.stderr or "")
    assert r.returncode == 0, f"resize failed:\n{out[-1500:]}"


def test_full_semaphore_test_file_passes():
    """p2p: the entire semaphore.test.ts file passes (covers all existing
    semaphore tests at once).
    """
    r = _run_vitest("test/Effect/semaphore.test.ts", timeout=600)
    out = (r.stdout or "") + (r.stderr or "")
    assert r.returncode == 0, f"semaphore.test.ts failed:\n{out[-1500:]}"


# ───────────────────────── style / agent-config ───────────────────────────────

def test_changeset_present():
    """agent-config: AGENTS.md mandates a changeset for every PR (.changeset/
    directory). The fix must include one.
    """
    cs_dir = REPO / ".changeset"
    assert cs_dir.is_dir()
    md_files = [
        p for p in cs_dir.glob("*.md")
        if p.name.lower() not in ("readme.md",)
    ]
    leak_changesets = []
    for p in md_files:
        text = p.read_text()
        head = text.splitlines()[:2]
        if any('"effect"' in line for line in head):
            if "semaphore" in text.lower() or "permit" in text.lower() or "leak" in text.lower():
                leak_changesets.append(p)
    assert leak_changesets, (
        "no changeset file mentioning the semaphore/permit fix found in "
        f".changeset/ — found {len(md_files)} changeset(s)"
    )


def test_no_extraneous_comments_added():
    """agent-config: AGENTS.md says 'Avoid comments unless absolutely required'.
    Ensure the fix doesn't add new // line comments inside the take/observer
    bodies (jsdoc /** */ blocks are exempt).
    """
    src = (PKG / "src" / "internal" / "effect" / "circular.ts").read_text()
    take_start = src.index("readonly take = (n: number)")
    take_end = src.index("updateTakenUnsafe", take_start)
    take_body = src[take_start:take_end]
    line_comments = [
        ln for ln in take_body.splitlines()
        if ln.strip().startswith("//")
    ]
    assert not line_comments, (
        "Semaphore.take should not contain explanatory // line comments "
        f"(AGENTS.md: avoid comments). Found: {line_comments}"
    )
