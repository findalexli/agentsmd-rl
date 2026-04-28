"""Behavioral tests for effect-ts/effect#6097 — TupleWithRest post-rest index drift.

Each test exercises Schema decoding via the real `effect` source through tsx,
asserting on the decoded value or ParseError text. The bug (a `i += j`
accumulator inside the post-rest tail loop) causes tail elements after the
first to be skipped or read from the wrong slot. The fix replaces the
accumulator with `const index = i + j` so each tail position is checked
independently.
"""
from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/effect")


def _run_tsx(script: str, timeout: int = 240) -> tuple[int, str, str]:
    """Execute a TypeScript snippet in the effect repo via tsx and return
    (returncode, stdout, stderr)."""
    scratch = REPO / "scratchpad"
    scratch.mkdir(parents=True, exist_ok=True)
    path = scratch / f"_probe_{os.getpid()}.ts"
    path.write_text(textwrap.dedent(script))
    try:
        result = subprocess.run(
            ["pnpm", "exec", "tsx", str(path)],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        try:
            path.unlink()
        except OSError:
            pass
    return result.returncode, result.stdout, result.stderr


def _decode(schema_expr: str, input_literal: str) -> dict:
    """Build a Schema, decode the given literal, and return
    {"ok": bool, "value"|"msg": ...}."""
    script = f"""
        import * as S from "effect/Schema"
        import * as Either from "effect/Either"
        const schema = {schema_expr}
        const r = S.decodeUnknownEither(schema)({input_literal})
        if (Either.isRight(r)) {{
          process.stdout.write(JSON.stringify({{ ok: true, value: r.right }}))
        }} else {{
          process.stdout.write(JSON.stringify({{ ok: false, msg: r.left.toString() }}))
        }}
    """
    rc, out, err = _run_tsx(script)
    assert rc == 0, f"tsx exited {rc}\nstdout:\n{out}\nstderr:\n{err}"
    return json.loads(out.strip())


# --------------------------------------------------------------------------- #
# fail_to_pass — these expose the post-rest index drift bug                    #
# --------------------------------------------------------------------------- #


def test_post_rest_index_drift_fails_at_index_4():
    """Decoding ["a", true, "b", "1", "x"] against Tuple([String], Boolean,
    String, NumberFromString, NumberFromString) MUST report failure at
    index [4]. With the drift bug, the slot is skipped and the call wrongly
    succeeds, dropping the trailing element."""
    r = _decode(
        'S.Tuple([S.String], S.Boolean, S.String, S.NumberFromString, S.NumberFromString)',
        '["a", true, "b", "1", "x"]',
    )
    assert r["ok"] is False, f"Decoding must fail; instead got value={r.get('value')}"
    msg = r["msg"]
    assert "[4]" in msg, f"Error must localise to index [4]; got:\n{msg}"
    assert '"x"' in msg, f"Error must mention the offending value 'x'; got:\n{msg}"


def test_post_rest_index_drift_succeeds_with_full_arity():
    """Decoding ["a", true, "b", "1", "2"] against the same schema MUST
    yield all five decoded elements ["a", true, "b", 1, 2]. With the bug,
    the last tail element is silently dropped."""
    r = _decode(
        'S.Tuple([S.String], S.Boolean, S.String, S.NumberFromString, S.NumberFromString)',
        '["a", true, "b", "1", "2"]',
    )
    assert r["ok"] is True, f"Decoding must succeed; got error:\n{r.get('msg')}"
    assert r["value"] == ["a", True, "b", 1, 2], (
        f"Decoded value must include every post-rest element; got: {r['value']}"
    )


def test_post_rest_index_drift_long_tail_succeeds():
    """A different shape — Tuple([NumberFromString], String,
    NumberFromString, NumberFromString, NumberFromString) — with a longer
    rest section must still decode every tail position. With the bug, the
    last tail slot is skipped (the j-accumulator overshoots `len`)."""
    r = _decode(
        'S.Tuple([S.NumberFromString], S.String, S.NumberFromString, S.NumberFromString, S.NumberFromString)',
        '["1", "a", "b", "2", "3", "4"]',
    )
    assert r["ok"] is True, f"Decoding must succeed; got error:\n{r.get('msg')}"
    assert r["value"] == [1, "a", "b", 2, 3, 4], (
        f"All six decoded elements expected; got: {r['value']}"
    )


def test_post_rest_index_drift_long_tail_fails_at_last_index():
    """Same shape as above with an invalid last element ('z') — failure
    MUST localise to index [5]. With the bug the offending slot is skipped
    and decoding wrongly succeeds with a 5-element output."""
    r = _decode(
        'S.Tuple([S.NumberFromString], S.String, S.NumberFromString, S.NumberFromString, S.NumberFromString)',
        '["1", "a", "b", "2", "3", "z"]',
    )
    assert r["ok"] is False, f"Decoding must fail; instead got value={r.get('value')}"
    msg = r["msg"]
    assert "[5]" in msg, f"Error must localise to index [5]; got:\n{msg}"
    assert '"z"' in msg, f"Error must mention the offending value 'z'; got:\n{msg}"


# --------------------------------------------------------------------------- #
# pass_to_pass — repo-side regression coverage                                 #
# --------------------------------------------------------------------------- #


def test_existing_tuple_vitest_suite_passes():
    """The repo's existing Tuple.test.ts must still pass — the fix must not
    regress any other tuple-decoding behavior."""
    r = subprocess.run(
        [
            "pnpm", "exec", "vitest", "run",
            "packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts",
            "--reporter=basic",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"vitest suite failed (rc={r.returncode})\n"
        f"--- STDOUT (last 2000 chars) ---\n{r.stdout[-2000:]}\n"
        f"--- STDERR (last 2000 chars) ---\n{r.stderr[-2000:]}"
    )


def test_effect_package_typecheck_passes():
    """The repo's TypeScript build for the effect package must still
    succeed — the fix must remain type-correct."""
    r = subprocess.run(
        ["pnpm", "--filter", "effect", "exec", "tsc", "-b", "tsconfig.json"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"tsc -b failed (rc={r.returncode})\n"
        f"--- STDOUT ---\n{r.stdout[-2000:]}\n"
        f"--- STDERR ---\n{r.stderr[-2000:]}"
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

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_String_Boolean_String_Number_Number_validates_ev():
    """fail_to_pass | PR added test '[String] + [Boolean, String, Number, Number] validates every post-rest index' in 'packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts" -t "[String] + [Boolean, String, Number, Number] validates every post-rest index" 2>&1 || npx vitest run "packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts" -t "[String] + [Boolean, String, Number, Number] validates every post-rest index" 2>&1 || pnpm jest "packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts" -t "[String] + [Boolean, String, Number, Number] validates every post-rest index" 2>&1 || npx jest "packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts" -t "[String] + [Boolean, String, Number, Number] validates every post-rest index" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test '[String] + [Boolean, String, Number, Number] validates every post-rest index' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
