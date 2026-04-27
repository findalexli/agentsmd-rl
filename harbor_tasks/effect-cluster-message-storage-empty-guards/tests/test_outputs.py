"""Behavioral tests for effect-cluster MessageStorage empty-id-list guards.

f2p tests verify that `makeEncoded` guards empty id lists before delegating
to the underlying encoded layer (using `Effect.die` traps to detect calls).
p2p tests run the repo's own existing test file plus type-check and lint.

The verifier vitest test is written into the repo only for the duration of
the vitest run — the file is removed before lint/typecheck so it does not
pollute repository checks.
"""
import json
import subprocess
from functools import lru_cache
from pathlib import Path

REPO = Path("/workspace/effect")
CLUSTER = REPO / "packages/cluster"
GUARD_TEST_FILE = CLUSTER / "test/_GuardsVerifier.test.ts"
GUARD_JSON_OUT = Path("/tmp/vitest_guards.json")

GUARD_TEST_CONTENT = """import { MessageStorage, Snowflake } from "@effect/cluster"
import { describe, expect, it } from "@effect/vitest"
import { Effect, Option } from "effect"

const baseEncoded = (overrides: Record<string, any> = {}): any => ({
  saveEnvelope: () => Effect.succeed(MessageStorage.SaveResultEncoded.Success()),
  saveReply: () => Effect.void,
  clearReplies: () => Effect.void,
  requestIdForPrimaryKey: () => Effect.succeed(Option.none()),
  repliesFor: () => Effect.succeed([]),
  repliesForUnfiltered: () => Effect.die("unexpected repliesForUnfiltered call"),
  unprocessedMessages: () => Effect.succeed([]),
  unprocessedMessagesById: () => Effect.succeed([]),
  resetAddress: () => Effect.void,
  clearAddress: () => Effect.void,
  resetShards: () => Effect.die("unexpected resetShards call"),
  ...overrides
})

describe("GuardsVerifier", () => {
  it.effect("repliesForUnfiltered_empty_returns_empty_without_delegating", () =>
    Effect.gen(function*() {
      const storage = yield* MessageStorage.makeEncoded(baseEncoded()).pipe(
        Effect.provide(Snowflake.layerGenerator)
      )
      const replies = yield* (storage.repliesForUnfiltered as any)([])
      expect(replies).toEqual([])
    }))

  it.effect("resetShards_empty_succeeds_without_delegating", () =>
    Effect.gen(function*() {
      const storage = yield* MessageStorage.makeEncoded(baseEncoded()).pipe(
        Effect.provide(Snowflake.layerGenerator)
      )
      yield* (storage.resetShards as any)([])
    }))

  it.effect("repliesForUnfiltered_nonempty_does_delegate", () =>
    Effect.gen(function*() {
      let receivedIds: ReadonlyArray<string> | null = null
      const storage = yield* MessageStorage.makeEncoded(baseEncoded({
        repliesForUnfiltered: (ids: ReadonlyArray<string>) => {
          receivedIds = ids as ReadonlyArray<string>
          return Effect.succeed([])
        }
      })).pipe(Effect.provide(Snowflake.layerGenerator))
      yield* (storage.repliesForUnfiltered as any)([
        Snowflake.Snowflake(BigInt(1)),
        Snowflake.Snowflake(BigInt(2))
      ])
      expect(receivedIds).toEqual(["1", "2"])
    }))

  it.effect("resetShards_nonempty_does_delegate", () =>
    Effect.gen(function*() {
      let receivedIds: ReadonlyArray<string> | null = null
      const storage = yield* MessageStorage.makeEncoded(baseEncoded({
        resetShards: (ids: ReadonlyArray<string>) => {
          receivedIds = ids as ReadonlyArray<string>
          return Effect.void
        }
      })).pipe(Effect.provide(Snowflake.layerGenerator))
      yield* (storage.resetShards as any)([{ toString: () => "11" }, { toString: () => "22" }])
      expect(receivedIds).toEqual(["11", "22"])
    }))
})
"""


@lru_cache(maxsize=1)
def _guards_results():
    """Write the verifier .test.ts file, run vitest with JSON reporter, then
    immediately delete the file. Cache the parsed results so subsequent f2p
    tests reuse them; cleanup ensures lint/typecheck checks see a clean tree.
    """
    GUARD_TEST_FILE.write_text(GUARD_TEST_CONTENT)
    try:
        if GUARD_JSON_OUT.exists():
            GUARD_JSON_OUT.unlink()
        cmd = [
            "pnpm", "vitest", "run",
            "--reporter=json",
            f"--outputFile={GUARD_JSON_OUT}",
            f"test/{GUARD_TEST_FILE.name}",
        ]
        proc = subprocess.run(
            cmd, cwd=CLUSTER, capture_output=True, text=True, timeout=600
        )
        data = None
        if GUARD_JSON_OUT.exists():
            try:
                data = json.loads(GUARD_JSON_OUT.read_text())
            except json.JSONDecodeError:
                pass
        return proc, data
    finally:
        if GUARD_TEST_FILE.exists():
            GUARD_TEST_FILE.unlink()
        if GUARD_JSON_OUT.exists():
            GUARD_JSON_OUT.unlink()


def _assertion_status(data, name_substring):
    if not data:
        return None
    for f in data.get("testResults", []):
        for a in f.get("assertionResults", []):
            full = (a.get("fullName") or "") + " " + (a.get("title") or "")
            if name_substring in full:
                return a.get("status")
    return None


def test_repliesForUnfiltered_empty_skips_delegation():
    proc, data = _guards_results()
    status = _assertion_status(data, "repliesForUnfiltered_empty_returns_empty_without_delegating")
    assert status == "passed", (
        f"Expected guard test to pass; got status={status!r}.\n"
        f"vitest stdout (last 3KB):\n{proc.stdout[-3000:]}\n"
        f"vitest stderr (last 2KB):\n{proc.stderr[-2000:]}"
    )


def test_resetShards_empty_skips_delegation():
    proc, data = _guards_results()
    status = _assertion_status(data, "resetShards_empty_succeeds_without_delegating")
    assert status == "passed", (
        f"Expected guard test to pass; got status={status!r}.\n"
        f"vitest stdout:\n{proc.stdout[-3000:]}\n"
        f"vitest stderr:\n{proc.stderr[-2000:]}"
    )


def test_repliesForUnfiltered_nonempty_still_delegates():
    proc, data = _guards_results()
    status = _assertion_status(data, "repliesForUnfiltered_nonempty_does_delegate")
    assert status == "passed", (
        f"Expected non-empty delegation test to pass; got status={status!r}.\n"
        f"vitest stdout:\n{proc.stdout[-3000:]}"
    )


def test_resetShards_nonempty_still_delegates():
    proc, data = _guards_results()
    status = _assertion_status(data, "resetShards_nonempty_does_delegate")
    assert status == "passed", (
        f"Expected non-empty delegation test to pass; got status={status!r}.\n"
        f"vitest stdout:\n{proc.stdout[-3000:]}"
    )


def test_repo_messagestorage_tests_pass():
    """p2p: existing MessageStorage.test.ts (6 at base / 7 at gold) all pass."""
    if GUARD_TEST_FILE.exists():
        GUARD_TEST_FILE.unlink()
    r = subprocess.run(
        ["pnpm", "vitest", "run", "test/MessageStorage.test.ts"],
        cwd=CLUSTER, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"Existing MessageStorage tests failed (rc={r.returncode}):\n"
        f"{r.stdout[-3000:]}\n{r.stderr[-1500:]}"
    )


def test_repo_typecheck_passes():
    """p2p: pnpm check (tsc) succeeds for the cluster package."""
    if GUARD_TEST_FILE.exists():
        GUARD_TEST_FILE.unlink()
    r = subprocess.run(
        ["pnpm", "check"],
        cwd=CLUSTER, capture_output=True, text=True, timeout=900,
    )
    assert r.returncode == 0, (
        f"pnpm check failed (rc={r.returncode}):\n"
        f"{r.stdout[-3000:]}\n{r.stderr[-1500:]}"
    )


def test_repo_lint_passes():
    """p2p: eslint passes for cluster package."""
    if GUARD_TEST_FILE.exists():
        GUARD_TEST_FILE.unlink()
    r = subprocess.run(
        ["pnpm", "lint", "packages/cluster"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"pnpm lint failed (rc={r.returncode}):\n"
        f"{r.stdout[-3000:]}\n{r.stderr[-1500:]}"
    )
