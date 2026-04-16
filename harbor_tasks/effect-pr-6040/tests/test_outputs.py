"""
Benchmark tests for effect-ts/effect#6040:
Fix Stream.decodeText to correctly handle multi-byte UTF-8 characters split across chunk boundaries.
"""

import subprocess
import os
import tempfile

REPO = "/workspace/effect"


def _run_ts(code: str, timeout: int = 120) -> tuple[int, str, str]:
    """Run TypeScript code via tsx and return (returncode, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            ["npx", "tsx", tmp],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout, r.stderr
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Fail-to-Pass: multi-byte UTF-8 split across chunks
# ---------------------------------------------------------------------------

def test_decodetext_multibyte_split_chunks():
    """
    Stream.decodeText must correctly decode a multi-byte UTF-8 character
    (e.g. 🌍 = 4 bytes) when those bytes are split across two Stream chunks.

    Without the { stream: true } fix, TextDecoder treats each chunk independently
    and fails to reconstruct the full character, producing wrong output or errors.
    With the fix, the decoder buffers incomplete sequences and completes them
    on the next call.
    """
    code = """
import * as Chunk from "effect/Chunk";
import * as Effect from "effect/Effect";
import { pipe } from "effect/Function";
import * as Stream from "effect/Stream";

// Test: 🌍 (4-byte emoji) split into two 2-byte chunks
const bytes = new TextEncoder().encode("🌍");
const stream = pipe(
  Stream.fromChunks(
    Chunk.of(bytes.slice(0, 2)),
    Chunk.of(bytes.slice(2, 4))
  ),
  Stream.decodeText(),
  Stream.mkString
);

Effect.runPromise(pipe(
  stream,
  Effect.map((s: string) => {
    if (s !== "🌍") {
      throw new Error(`Expected "🌍" but got "${s}"`);
    }
    console.log("OK");
  })
));
"""
    rc, stdout, stderr = _run_ts(code)
    combined = stdout + stderr
    assert rc == 0, f"decodeText multi-byte split failed (exit {rc}):\n{combined}"
    assert "OK" in combined, f"Test did not pass cleanly:\n{combined}"


def test_decodetext_mixed_ascii_multibyte():
    """
    Stream.decodeText must correctly decode mixed ASCII and multi-byte UTF-8
    characters when the boundary falls mid-character across two Stream chunks.

    E.g. "Hello 🌍!" with 🌍 split at a byte boundary.
    Without the fix, the split 🌍 bytes become replacement characters or errors.
    """
    code = """
import * as Chunk from "effect/Chunk";
import * as Effect from "effect/Effect";
import { pipe } from "effect/Function";
import * as Stream from "effect/Stream";

// Test: "Hello 🌍!" where 🌍 (4 bytes) starts at byte 6 and is split
const bytes = new TextEncoder().encode("Hello 🌍!");
const splitPoint = 8; // cut after "Hello " (6 ASCII bytes + 2 bytes of 🌍)
const stream = pipe(
  Stream.fromChunks(
    Chunk.of(bytes.slice(0, splitPoint)),
    Chunk.of(bytes.slice(splitPoint))
  ),
  Stream.decodeText(),
  Stream.mkString
);

Effect.runPromise(pipe(
  stream,
  Effect.map((s: string) => {
    if (s !== "Hello 🌍!") {
      throw new Error(`Expected "Hello 🌍!" but got "${s}"`);
    }
    console.log("OK");
  })
));
"""
    rc, stdout, stderr = _run_ts(code)
    combined = stdout + stderr
    assert rc == 0, f"decodeText mixed ASCII/multi-byte failed (exit {rc}):\n{combined}"
    assert "OK" in combined, f"Test did not pass cleanly:\n{combined}"


def test_decodetext_many_multibyte_splits():
    """
    Stream.decodeText must handle multiple multi-byte characters each split
    across chunk boundaries in a long stream.
    """
    code = """
import * as Chunk from "effect/Chunk";
import * as Effect from "effect/Effect";
import { pipe } from "effect/Function";
import * as Stream from "effect/Stream";

// Three 4-byte emojis: 🌍 🌎 🌏 (each split into two 2-byte chunks)
const emojis = "🌍🌎🌏";
const bytes = new TextEncoder().encode(emojis);
const chunks: Chunk.Chunk<Uint8Array>[] = [];
for (let i = 0; i < bytes.length; i += 2) {
  chunks.push(Chunk.of(bytes.slice(i, i + 2)));
}

const stream = pipe(
  Stream.fromChunks(...chunks),
  Stream.decodeText(),
  Stream.mkString
);

Effect.runPromise(pipe(
  stream,
  Effect.map((s: string) => {
    if (s !== emojis) {
      throw new Error(`Expected "${emojis}" but got "${s}"`);
    }
    console.log("OK");
  })
));
"""
    rc, stdout, stderr = _run_ts(code)
    combined = stdout + stderr
    assert rc == 0, f"decodeText many multibyte splits failed (exit {rc}):\n{combined}"
    assert "OK" in combined, f"Test did not pass cleanly:\n{combined}"


# ---------------------------------------------------------------------------
# Pass-to-Pass: repo's own encoding tests
# ---------------------------------------------------------------------------

def test_repo_encoding_tests():
    """
    The repo's own encoding test suite (packages/effect/test/Stream/encoding.test.ts)
    must pass. This is a pass_to_pass check: it should pass both before and after
    the fix (since the fix adds new passing tests, not breaks existing ones).
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "packages/effect/test/Stream/encoding.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # The new tests added by the PR should pass; existing tests should continue passing
    assert r.returncode == 0, f"Encoding tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}"


def test_pnpm_check():
    """
    pnpm check (type checking) must pass on the fixed code.
    This is pass_to_pass: type checking should succeed both before and after.
    """
    r = subprocess.run(
        ["pnpm", "check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"pnpm check failed:\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}"


def test_pnpm_lint():
    """
    pnpm lint must pass on the fixed code.
    This is pass_to_pass: linting should succeed both before and after.
    """
    r = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}"


def test_pnpm_circular():
    """
    pnpm circular (circular dependency check) must pass.
    This is pass_to_pass: circular deps should be caught regardless of fix.
    """
    r = subprocess.run(
        ["pnpm", "circular"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"circular deps check failed:\n{r.stdout[-500:]}"


def test_pnpm_codegen():
    """
    pnpm codegen must run without producing diffs (code is up to date).
    This is pass_to_pass: codegen should be clean.
    """
    # Capture the diff BEFORE codegen runs (there may be existing changes from the fix)
    r_diff_before = subprocess.run(
        ["git", "diff"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    diff_before = r_diff_before.stdout

    r = subprocess.run(
        ["pnpm", "codegen"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"codegen failed:\n{r.stdout[-500:]}"

    # Verify no NEW file changes after codegen (beyond what existed before)
    r_diff_after = subprocess.run(
        ["git", "diff"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    diff_after = r_diff_after.stdout

    # Codegen should not introduce additional changes beyond what was already there
    assert diff_after == diff_before, f"codegen produced new file changes:\n{diff_after}"


def test_pnpm_check_recursive():
    """
    pnpm check-recursive (recursive type checking across all packages) must pass.
    This is pass_to_pass: all packages should type-check.
    """
    r = subprocess.run(
        ["pnpm", "check-recursive"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"check-recursive failed:\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}"


def test_pnpm_test_types():
    """
    pnpm test-types (tstyche type-checking tests) must pass.
    This is pass_to_pass: type-level tests should pass on base commit.
    """
    r = subprocess.run(
        ["pnpm", "test-types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"test-types failed:\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}"
