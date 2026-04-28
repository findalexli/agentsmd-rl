"""Behavioral tests for Stream.changes / changesWith empty-chunk fix.

The PR being graded prevents Stream.changes (and changesWith) from emitting
empty chunks downstream when every element of an input chunk is filtered out
as a duplicate of the previously seen value. The bug is observable by piping
through Stream.chunks and checking for chunks of length 0.
"""

import json
import os
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/effect"
PKG = "packages/effect"
TEST_DIR = f"{REPO}/{PKG}/test/Stream"

# Marker test file we drop into the repo's test tree so vitest picks it up.
F2P_TEST_FILE = "changes_empty_chunk_regression.test.ts"

F2P_TEST_SOURCE = r"""import { describe, it } from "@effect/vitest"
import { strictEqual, deepStrictEqual } from "@effect/vitest/utils"
import * as Chunk from "effect/Chunk"
import * as Effect from "effect/Effect"
import { pipe } from "effect/Function"
import * as Stream from "effect/Stream"

describe("Stream.changes empty-chunk regression", () => {
  it.effect("does not emit empty chunks when whole chunk is duplicates", () =>
    Effect.gen(function*() {
      const stream = Stream.fromChunks(
        Chunk.of(1),
        Chunk.make(1, 1),
        Chunk.of(2)
      )
      const chunks = yield* pipe(stream, Stream.changes, Stream.chunks, Stream.runCollect)
      const sizes = Array.from(chunks).map((c) => c.length)
      strictEqual(sizes.includes(0), false)
    }))

  it.effect("does not emit empty chunks for several consecutive duplicate-only chunks", () =>
    Effect.gen(function*() {
      const stream = Stream.fromChunks(
        Chunk.of(7),
        Chunk.make(7, 7, 7),
        Chunk.make(7, 7),
        Chunk.of(8),
        Chunk.make(8, 8),
        Chunk.of(9)
      )
      const chunks = yield* pipe(stream, Stream.changes, Stream.chunks, Stream.runCollect)
      const sizes = Array.from(chunks).map((c) => c.length)
      strictEqual(sizes.includes(0), false)
      const flattened = Array.from(chunks).flatMap((c) => Array.from(c))
      deepStrictEqual(flattened, [7, 8, 9])
    }))

  it.effect("changesWith with custom equality also skips empty chunks", () =>
    Effect.gen(function*() {
      const stream = Stream.fromChunks(
        Chunk.of("a"),
        Chunk.make("A", "a", "A"),
        Chunk.of("b")
      )
      const chunks = yield* pipe(
        stream,
        Stream.changesWith((x: string, y: string) => x.toLowerCase() === y.toLowerCase()),
        Stream.chunks,
        Stream.runCollect
      )
      const sizes = Array.from(chunks).map((c) => c.length)
      strictEqual(sizes.includes(0), false)
    }))

  it.effect("Stream.changes still produces correct distinct sequence", () =>
    Effect.gen(function*() {
      const stream = Stream.fromChunks(
        Chunk.make(1, 1, 2),
        Chunk.make(2, 2),
        Chunk.make(3, 3, 3),
        Chunk.make(3, 4)
      )
      const result = yield* pipe(stream, Stream.changes, Stream.runCollect)
      deepStrictEqual(Array.from(result), [1, 2, 3, 4])
    }))
})
"""


def _ensure_f2p_test_file_present() -> Path:
    Path(TEST_DIR).mkdir(parents=True, exist_ok=True)
    target = Path(TEST_DIR) / F2P_TEST_FILE
    target.write_text(F2P_TEST_SOURCE)
    return target


def _run_vitest(test_relpath: str, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a single vitest file inside packages/effect.

    Use pnpm --filter effect to run only the effect package's vitest.
    """
    cmd = ["pnpm", "--filter", "effect", "exec", "vitest", "run", test_relpath, "--reporter=default"]
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "true"},
    )


# ---------------------------------------------------------------------------
# Fail-to-pass
# ---------------------------------------------------------------------------

def test_changes_empty_chunk_regression_passes():
    """The custom regression suite must pass (fails on base, passes on fix)."""
    _ensure_f2p_test_file_present()
    proc = _run_vitest(f"test/Stream/{F2P_TEST_FILE}")
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    assert proc.returncode == 0, (
        "regression test suite should pass after fix; vitest output (last 3000 chars):\n"
        + out[-3000:]
    )


def test_no_empty_chunks_emitted_via_inline_script():
    """Direct tsx-runnable assertion: Stream.changes must not emit empty chunks.

    Independent of vitest: compiles and runs an inline TypeScript program via
    tsx that constructs a stream where one input chunk is 100% duplicates and
    asserts the resulting chunk emission contains no zero-length chunks.
    """
    script_path = Path(REPO) / "scratchpad" / "empty_chunk_probe.ts"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(textwrap.dedent(r"""
        import * as Chunk from "effect/Chunk"
        import * as Effect from "effect/Effect"
        import { pipe } from "effect/Function"
        import * as Stream from "effect/Stream"

        const program = pipe(
          Stream.fromChunks(Chunk.of(1), Chunk.make(1, 1), Chunk.of(2)),
          Stream.changes,
          Stream.chunks,
          Stream.runCollect
        )

        const chunks = Effect.runSync(program)
        const sizes = Array.from(chunks).map((c) => c.length)
        const flattened = Array.from(chunks).flatMap((c) => Array.from(c))

        const result = { sizes, flattened }
        process.stdout.write("RESULT=" + JSON.stringify(result) + "\n")
        if (sizes.includes(0)) {
          process.stderr.write("FAILURE: empty chunk emitted\n")
          process.exit(1)
        }
        if (flattened.join(",") !== "1,2") {
          process.stderr.write("FAILURE: distinct sequence wrong: " + flattened.join(",") + "\n")
          process.exit(2)
        }
        process.exit(0)
    """).strip() + "\n")

    cmd = ["pnpm", "exec", "tsx", str(script_path)]
    proc = subprocess.run(
        cmd, cwd=f"{REPO}/{PKG}", capture_output=True, text=True, timeout=180
    )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    assert proc.returncode == 0, (
        "tsx probe must succeed (no empty chunks). Output:\n" + out[-2000:]
    )
    assert "RESULT=" in proc.stdout, "expected RESULT= line in stdout"


# ---------------------------------------------------------------------------
# Pass-to-pass — repo's own behavior must remain intact
# ---------------------------------------------------------------------------

def test_existing_changing_test_still_passes():
    """Repo's own packages/effect/test/Stream/changing.test.ts still passes."""
    proc = _run_vitest("test/Stream/changing.test.ts")
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    assert proc.returncode == 0, (
        "existing changing.test.ts must still pass; output:\n" + out[-2000:]
    )


def test_typecheck_target_file():
    """Type-check the patched file in isolation: tsc on packages/effect must succeed.

    Uses the project's own tsc build config (tsconfig.json) to verify the
    patched stream.ts still type-checks. This is a p2p check — it should be
    green on both base and fix; it guards against fixes that introduce a type
    error.
    """
    proc = subprocess.run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.json", "--pretty", "false"],
        cwd=f"{REPO}/{PKG}",
        capture_output=True,
        text=True,
        timeout=600,
    )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    assert proc.returncode == 0, "pnpm check (tsc) must pass; output:\n" + out[-3000:]


def test_no_index_ts_modified():
    """AGENTS.md: index.ts barrel files must not be hand-edited.

    Verify HEAD's diff vs. base does not touch any index.ts under
    packages/effect/src/. (Agent config rule: index files are codegen-only.)
    """
    base = "ed4531817716dbf52e1d59ac4d3614ef5a1dae71"
    proc = subprocess.run(
        ["git", "diff", "--name-only", base, "--", "packages/effect/src/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    changed = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    barrel_changes = [p for p in changed if p.endswith("/index.ts") or p.endswith("src/index.ts")]
    assert not barrel_changes, (
        "AGENTS.md forbids hand-editing index.ts barrel files; changed:\n"
        + "\n".join(barrel_changes)
    )


def test_changeset_added():
    """AGENTS.md: every PR must add a changeset under .changeset/."""
    base = "ed4531817716dbf52e1d59ac4d3614ef5a1dae71"
    proc = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", base, "--", ".changeset/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    added = [
        line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().endswith(".md") and "/README" not in line
    ]
    assert added, (
        "AGENTS.md requires a changeset (.changeset/*.md) for every PR; none found."
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_pnpm():
    """pass_to_pass | CI job 'Build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docgen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

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