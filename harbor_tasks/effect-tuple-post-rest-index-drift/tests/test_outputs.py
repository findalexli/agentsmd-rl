"""Behavior tests for Effect-TS PR #6097 — TupleWithRest post-rest validation.

Approach: write a small probe TypeScript file into the cloned monorepo's
`scratchpad/` directory, then execute it through `pnpm tsx` from inside
`packages/effect`. The probe exercises the schema decoder against several
tuples-with-rest, dumps a structured JSON report to stdout, and we assert
on each case from individual pytest functions.

The PR fixes an off-by-one (cumulative) error in post-rest tail validation:
the loop variable was being mutated cumulatively (`i += j`) instead of
using a per-iteration local index (`const index = i + j`). For tails of
length >= 3 (or length >= 4 when the rest matches multiple elements), some
post-rest indices are no longer validated, so invalid inputs silently
"succeed" or report errors at wrong indices.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/effect")
EFFECT_PKG = REPO / "packages" / "effect"
PROBE_REL = "scratchpad/_post_rest_probe.ts"
PROBE_PATH = REPO / PROBE_REL


PROBE_SOURCE = r"""// Probe for Effect-TS PR #6097: post-rest tuple validation index drift.
import * as S from "effect/Schema"
import * as ParseResult from "effect/ParseResult"
import { Either } from "effect"

type Result =
    | { name: string; kind: "right"; value: unknown }
    | { name: string; kind: "left"; message: string }

const out: Result[] = []

function record(name: string, run: () => unknown) {
    try {
        const r = run() as any
        if (Either.isRight(r)) {
            out.push({ name, kind: "right", value: r.right })
        } else {
            out.push({
                name,
                kind: "left",
                message: ParseResult.TreeFormatter.formatErrorSync(r.left),
            })
        }
    } catch (e: any) {
        out.push({ name, kind: "left", message: "THREW: " + (e?.message ?? String(e)) })
    }
}

// Case A: head=[String], rest=Boolean, tail=[String, NumberFromString, NumberFromString]
// Inputs taken from the PR's added test plus variations.
const schemaA = S.Tuple(
    [S.String],
    S.Boolean,
    S.String,
    S.NumberFromString,
    S.NumberFromString,
)

// Should fail: index 4 has "x" which is not a number.
record("A_invalid_at_4", () =>
    S.decodeUnknownEither(schemaA)(["a", true, "b", "1", "x"]))

// Should succeed: all valid.
record("A_all_valid", () =>
    S.decodeUnknownEither(schemaA)(["a", true, "b", "1", "2"]))

// Should fail: index 3 has "y" (not a number). Different position.
record("A_invalid_at_3", () =>
    S.decodeUnknownEither(schemaA)(["a", true, "b", "y", "2"]))

// Should fail: index 2 has 9 (number, not string).
record("A_invalid_at_2", () =>
    S.decodeUnknownEither(schemaA)(["a", true, 9, "1", "2"]))

// Case B: head=[], rest=Number, tail=[String, String, String, NumberFromString]
// 4 post-rest tail elements — exercises drift past index 2.
const schemaB = S.Tuple(
    [],
    S.Number,
    S.String,
    S.String,
    S.String,
    S.NumberFromString,
)

// Length 7: 3 rest numbers, then [String, String, String, NumberFromString].
// Should fail at index 6 ("nope").
record("B_invalid_at_6", () =>
    S.decodeUnknownEither(schemaB)([1, 2, 3, "x", "y", "z", "nope"]))

// Should succeed.
record("B_all_valid", () =>
    S.decodeUnknownEither(schemaB)([1, 2, 3, "x", "y", "z", "42"]))

// Should fail at index 5 (string expected, got 7).
record("B_invalid_at_5", () =>
    S.decodeUnknownEither(schemaB)([1, 2, 3, "x", "y", 7, "42"]))

console.log("===PROBE_BEGIN===")
console.log(JSON.stringify(out, null, 2))
console.log("===PROBE_END===")
"""


def _ensure_probe() -> None:
    PROBE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROBE_PATH.write_text(PROBE_SOURCE)


def _run_probe() -> list[dict]:
    _ensure_probe()
    r = subprocess.run(
        ["pnpm", "exec", "tsx", str(PROBE_PATH)],
        cwd=EFFECT_PKG,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"probe failed (exit {r.returncode}):\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr[-1500:]}"
        )
    out = r.stdout
    start = out.find("===PROBE_BEGIN===")
    end = out.find("===PROBE_END===")
    if start < 0 or end < 0:
        raise RuntimeError(f"probe markers missing in output:\n{out}")
    payload = out[start + len("===PROBE_BEGIN===") : end].strip()
    return json.loads(payload)


@pytest.fixture(scope="module")
def probe_results() -> dict[str, dict]:
    rs = _run_probe()
    return {r["name"]: r for r in rs}


# ── fail_to_pass: behavioral tests for the bug ──────────────────────────────


def test_caseA_invalid_at_index_4_reports_index_4(probe_results):
    """Decoding ['a', true, 'b', '1', 'x'] must fail at index [4] with NumberFromString error."""
    r = probe_results["A_invalid_at_4"]
    assert r["kind"] == "left", (
        f"expected decode to FAIL but it succeeded with value: {r.get('value')!r}"
    )
    msg = r["message"]
    assert "[4]" in msg, f"error path should reference index [4], got:\n{msg}"
    assert "NumberFromString" in msg or "Unable to decode" in msg, (
        f"error should reference NumberFromString failure on 'x', got:\n{msg}"
    )


def test_caseA_all_valid_succeeds(probe_results):
    """Decoding the all-valid input must succeed and transform NumberFromString correctly."""
    r = probe_results["A_all_valid"]
    assert r["kind"] == "right", (
        f"expected decode to SUCCEED but it failed:\n{r.get('message')}"
    )
    assert r["value"] == ["a", True, "b", 1, 2], (
        f"decoded value mismatch — NumberFromString should produce numbers; got {r['value']!r}"
    )


def test_caseA_invalid_at_index_3_reports_index_3(probe_results):
    """Decoding ['a', true, 'b', 'y', '2'] must fail at index [3] (NumberFromString on 'y')."""
    r = probe_results["A_invalid_at_3"]
    assert r["kind"] == "left", (
        f"expected decode to FAIL but it succeeded with: {r.get('value')!r}"
    )
    assert "[3]" in r["message"], (
        f"error path should reference index [3], got:\n{r['message']}"
    )


def test_caseA_invalid_at_index_2_reports_index_2(probe_results):
    """Decoding ['a', true, 9, '1', '2'] must fail at index [2] (Expected string, got number)."""
    r = probe_results["A_invalid_at_2"]
    assert r["kind"] == "left", f"expected fail, got success: {r.get('value')!r}"
    assert "[2]" in r["message"], (
        f"error path should reference index [2], got:\n{r['message']}"
    )


def test_caseB_four_tail_elements_invalid_at_6(probe_results):
    """With 4 post-rest tail elements, the LAST tail position must still be validated."""
    r = probe_results["B_invalid_at_6"]
    assert r["kind"] == "left", (
        f"expected decode to FAIL on 'nope' at index 6, but got success: {r.get('value')!r}"
    )
    assert "[6]" in r["message"], (
        f"error path should reference index [6], got:\n{r['message']}"
    )


def test_caseB_all_valid_succeeds(probe_results):
    """Case B all-valid input decodes successfully; final NumberFromString produces 42."""
    r = probe_results["B_all_valid"]
    assert r["kind"] == "right", f"expected success, got fail:\n{r.get('message')}"
    assert r["value"] == [1, 2, 3, "x", "y", "z", 42], (
        f"unexpected decoded value: {r['value']!r}"
    )


def test_caseB_invalid_at_index_5(probe_results):
    """Index 5 of case B (third post-rest String) must fail when given a number."""
    r = probe_results["B_invalid_at_5"]
    assert r["kind"] == "left", f"expected fail, got success: {r.get('value')!r}"
    assert "[5]" in r["message"], (
        f"error path should reference index [5], got:\n{r['message']}"
    )


# ── pass_to_pass: regression on existing repo tests ─────────────────────────


def test_p2p_existing_tuple_tests_pass():
    """The repo's existing Tuple decoding/encoding tests must still pass at base + after fix."""
    r = subprocess.run(
        [
            "pnpm", "exec", "vitest", "run",
            "test/Schema/Schema/Tuple/Tuple.test.ts",
            "--reporter=basic",
            "--no-coverage",
        ],
        cwd=EFFECT_PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"existing Tuple.test.ts failed:\nSTDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )


def test_p2p_existing_parseresult_tests_pass():
    """The repo's existing ParseResult tests must still pass at base + after fix."""
    r = subprocess.run(
        [
            "pnpm", "exec", "vitest", "run",
            "test/Schema/ParseResult.test.ts",
            "--reporter=basic",
            "--no-coverage",
        ],
        cwd=EFFECT_PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"existing ParseResult.test.ts failed:\nSTDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )
