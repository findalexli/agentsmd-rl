"""Tests for effect-ts/effect PR 6040 — Stream.decodeText multi-byte chunk split.

The agent's task is to fix Stream.decodeText so it preserves the TextDecoder's
internal buffer across chunks. We verify the fix by:

  * Running 4 behavioral vitest tests that decode multi-byte UTF-8 characters
    split across chunk boundaries (fail-to-pass).
  * Running the pre-existing encoding round-trip test (pass-to-pass).
  * Running the repo's TypeScript build for the effect package (pass-to-pass).
  * Running the repo's eslint over the touched sources (pass-to-pass).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")
EFFECT_PKG = REPO / "packages" / "effect"
PR_TEST_DST = EFFECT_PKG / "test" / "Stream" / "decodetext_pr6040.test.ts"

PR_TEST_SRC = r"""import { describe, it } from "@effect/vitest"
import { strictEqual } from "@effect/vitest/utils"
import * as Chunk from "effect/Chunk"
import * as Effect from "effect/Effect"
import { pipe } from "effect/Function"
import * as Stream from "effect/Stream"

describe("Stream.decodeText (PR 6040)", () => {
  it.effect("4-byte UTF-8 character split across two chunks (emoji)", () =>
    Effect.gen(function*() {
      const bytes = new TextEncoder().encode("\u{1F30D}")
      const stream = Stream.fromChunks(
        Chunk.of(bytes.slice(0, 2)),
        Chunk.of(bytes.slice(2, 4))
      )
      const result = yield* pipe(stream, Stream.decodeText(), Stream.mkString)
      strictEqual(result, "\u{1F30D}")
    }))

  it.effect("3-byte UTF-8 character split across two chunks (euro sign)", () =>
    Effect.gen(function*() {
      const bytes = new TextEncoder().encode("€")
      const stream = Stream.fromChunks(
        Chunk.of(bytes.slice(0, 1)),
        Chunk.of(bytes.slice(1, 3))
      )
      const result = yield* pipe(stream, Stream.decodeText(), Stream.mkString)
      strictEqual(result, "€")
    }))

  it.effect("2-byte UTF-8 character split across two chunks (n-tilde)", () =>
    Effect.gen(function*() {
      const bytes = new TextEncoder().encode("ñ")
      const stream = Stream.fromChunks(
        Chunk.of(bytes.slice(0, 1)),
        Chunk.of(bytes.slice(1, 2))
      )
      const result = yield* pipe(stream, Stream.decodeText(), Stream.mkString)
      strictEqual(result, "ñ")
    }))

  it.effect("ASCII prefix plus multi-byte char split across chunks", () =>
    Effect.gen(function*() {
      const bytes = new TextEncoder().encode("Hello \u{1F30D}!")
      const splitPoint = 6 + 2
      const stream = Stream.fromChunks(
        Chunk.of(bytes.slice(0, splitPoint)),
        Chunk.of(bytes.slice(splitPoint))
      )
      const result = yield* pipe(stream, Stream.decodeText(), Stream.mkString)
      strictEqual(result, "Hello \u{1F30D}!")
    }))
})
"""


def _ensure_pr_test_in_repo() -> None:
    """Materialise the behavioural vitest fixture inside the cloned repo."""
    PR_TEST_DST.parent.mkdir(parents=True, exist_ok=True)
    PR_TEST_DST.write_text(PR_TEST_SRC, encoding="utf-8")


def _run_vitest_pattern(pattern: str, timeout: int = 180) -> subprocess.CompletedProcess:
    _ensure_pr_test_in_repo()
    return subprocess.run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "test/Stream/decodetext_pr6040.test.ts",
            "-t",
            pattern,
            "--reporter=default",
        ],
        cwd=str(EFFECT_PKG),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _assert_pattern_passes(pattern: str) -> None:
    r = _run_vitest_pattern(pattern)
    out = r.stdout + r.stderr
    assert r.returncode == 0, (
        f"vitest pattern {pattern!r} did not pass.\n"
        f"--- stdout (tail) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-1000:]}"
    )
    # Defensive: ensure at least one test actually ran (-t with no match passes by default).
    assert "Tests  1 passed" in out or " 1 passed" in out, (
        f"vitest pattern {pattern!r} matched zero tests.\n{out[-1500:]}"
    )


# -------------------- f2p behavioural tests --------------------


def test_decodeText_split_4byte_emoji():
    """4-byte UTF-8 character (earth-globe emoji) split across two chunks must round-trip."""
    _assert_pattern_passes("4-byte UTF-8 character split across two chunks")


def test_decodeText_split_3byte_euro():
    """3-byte UTF-8 character (euro sign) split across two chunks must round-trip."""
    _assert_pattern_passes("3-byte UTF-8 character split across two chunks")


def test_decodeText_split_2byte_ntilde():
    """2-byte UTF-8 character (n-tilde) split across two chunks must round-trip."""
    _assert_pattern_passes("2-byte UTF-8 character split across two chunks")


def test_decodeText_split_ascii_prefix_emoji():
    """ASCII prefix followed by a multi-byte char split mid-byte must round-trip."""
    _assert_pattern_passes("ASCII prefix plus multi-byte char split across chunks")


# -------------------- p2p (regression / repo CI) --------------------


def test_existing_encoding_round_trip():
    """Pre-existing Stream encoding round-trip test must still pass."""
    r = subprocess.run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "test/Stream/encoding.test.ts",
            "--reporter=default",
        ],
        cwd=str(EFFECT_PKG),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"encoding.test.ts failed.\n--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-1000:]}"
    )


def test_effect_package_typechecks():
    """`tsc -b tsconfig.json` for the effect package must succeed (zero TS errors)."""
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.json"],
        cwd=str(EFFECT_PKG),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"tsc -b reported errors.\n--- stdout ---\n{r.stdout[-2500:]}\n--- stderr ---\n{r.stderr[-1500:]}"
    )


def test_eslint_clean_on_changed_sources():
    """ESLint must report no errors on the source/test files in scope."""
    r = subprocess.run(
        [
            "pnpm",
            "exec",
            "eslint",
            "packages/effect/src/internal/stream.ts",
            "packages/effect/test/Stream/encoding.test.ts",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"eslint reported issues.\n--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-1000:]}"
    )
