"""Regression tests for effect-ts/effect#6086.

The fix adds a `case "Transformation"` branch to
`SchemaAST.getPropertyKeyIndexedAccess`. Before the fix,
`Schema.getPropertySignatures` throws "Unsupported schema (Transformation)"
on any Struct that contains `Schema.optionalWith(..., { default })` (or
similar Transformation-producing variants).

Tests call into the real source via vitest so the agent's edit to
`packages/effect/src/SchemaAST.ts` is exercised end-to-end.
"""

from __future__ import annotations

import os
import re
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/effect")
EFFECT_TEST_DIR = REPO / "packages/effect/test/Schema/SchemaAST"

# Tests we drop into the repo at runtime. Living here (not on disk in /tests/)
# means the agent never sees them.
GOLD_TEST_FILE = EFFECT_TEST_DIR / "__regression_pr6086.test.ts"

GOLD_TEST_TS = r"""
import { describe, it } from "@effect/vitest"
import { deepStrictEqual } from "@effect/vitest/utils"
import * as S from "effect/Schema"
import * as AST from "effect/SchemaAST"

describe("regression-pr6086:getPropertySignatures-transformation", () => {
  it("Struct with optionalWith({ default }) does not throw", () => {
    const schema = S.Struct({
      a: S.String,
      b: S.optionalWith(S.Number, { default: () => 0 })
    })
    // Must not throw "Unsupported schema (Transformation)".
    const sigs = AST.getPropertySignatures(schema.ast)
    deepStrictEqual(sigs.length, 2)
    deepStrictEqual(sigs[0].name, "a")
    deepStrictEqual(sigs[1].name, "b")
    deepStrictEqual(sigs[0].isReadonly, true)
    deepStrictEqual(sigs[1].isReadonly, true)
  })

  it("Struct with optionalWith({ as: 'Option' }) does not throw", () => {
    const schema = S.Struct({
      a: S.String,
      b: S.optionalWith(S.Number, { as: "Option" })
    })
    const sigs = AST.getPropertySignatures(schema.ast)
    deepStrictEqual(sigs.length, 2)
    deepStrictEqual(sigs[0].name, "a")
    deepStrictEqual(sigs[1].name, "b")
    // The decoded type for `b` is Option<number> — encoded as a Declaration node.
    deepStrictEqual(sigs[1].type._tag, "Declaration")
  })

  it("Struct with optionalWith({ nullable: true, default }) does not throw", () => {
    const schema = S.Struct({
      a: S.String,
      b: S.optionalWith(S.Number, { nullable: true, default: () => 0 })
    })
    const sigs = AST.getPropertySignatures(schema.ast)
    deepStrictEqual(sigs.length, 2)
    deepStrictEqual(sigs[0].name, "a")
    deepStrictEqual(sigs[1].name, "b")
  })
})
"""


def _write_gold_test() -> None:
    EFFECT_TEST_DIR.mkdir(parents=True, exist_ok=True)
    GOLD_TEST_FILE.write_text(textwrap.dedent(GOLD_TEST_TS).lstrip())


def _run_vitest(test_path: str, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "pnpm",
            "--filter=effect",
            "exec",
            "vitest",
            "run",
            test_path,
            "--reporter=default",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "1"},
    )


# ---------------------------------------------------------------------------
# Fail-to-pass: the Transformation regression
# ---------------------------------------------------------------------------


def test_f2p_optionalwith_default_does_not_throw():
    """getPropertySignatures must not throw on Struct with optionalWith({ default })."""
    _write_gold_test()
    r = _run_vitest("test/Schema/SchemaAST/__regression_pr6086.test.ts")
    combined = r.stdout + r.stderr
    assert r.returncode == 0, (
        "vitest failed on regression file (likely 'Unsupported schema "
        f"(Transformation)'):\n{combined[-2500:]}"
    )
    # Verify all 3 regression tests in the file passed (gold file has 3).
    assert "3 passed" in combined, (
        f"expected 3 passing tests in regression file:\n{combined[-1500:]}"
    )


def test_f2p_optionalwith_as_option_does_not_throw():
    """The Option variant test must pass — verified by re-running the file."""
    _write_gold_test()
    # Re-run; vitest is fast on cached transforms.
    r = _run_vitest("test/Schema/SchemaAST/__regression_pr6086.test.ts")
    combined = r.stdout + r.stderr
    assert r.returncode == 0, (
        f"vitest failed on optionalWith variants:\n{combined[-2500:]}"
    )
    # The error message that pre-fix code throws must not appear.
    assert "Unsupported schema" not in combined, (
        f"pre-fix error message appeared:\n{combined[-1500:]}"
    )


def test_f2p_no_unsupported_transformation_error():
    """The specific error message must not appear when running the regression tests."""
    _write_gold_test()
    r = _run_vitest("test/Schema/SchemaAST/__regression_pr6086.test.ts")
    combined = r.stdout + r.stderr
    assert "Unsupported schema (Transformation)" not in combined, (
        "the pre-fix error message appeared, fix is incomplete:\n"
        f"{combined[-2000:]}"
    )
    assert r.returncode == 0


# ---------------------------------------------------------------------------
# Pass-to-pass: existing repo tests still pass
# ---------------------------------------------------------------------------


def test_p2p_existing_getPropertySignatures_tests():
    """The 5 existing getPropertySignatures tests must still pass."""
    r = _run_vitest("test/Schema/SchemaAST/getPropertySignatures.test.ts")
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"existing tests broke:\n{combined[-2000:]}"
    # The existing file has 5 tests; use >= so the agent can add tests to
    # this file (as the PR author did) without breaking the p2p check.
    # Strip ANSI codes (vitest output is colorized even with CI=1).
    clean = re.sub(r"\x1b\[[0-9;]*m", "", combined)
    m = re.search(r"Tests\s+(\d+) passed", clean)
    assert m, f"no test summary found:\n{combined[-1500:]}"
    assert int(m.group(1)) >= 5, f"fewer than 5 tests ran:\n{combined[-1500:]}"


def test_p2p_sibling_schemaast_tests():
    """Sibling SchemaAST tests must still pass — broader p2p coverage.

    We list the existing test files explicitly (excluding our regression
    file) so the p2p stays valid even after `_write_gold_test()` ran. The
    paths are relative to `packages/effect/` because that's vitest's cwd
    when invoked via `pnpm --filter=effect`.
    """
    pkg_test_root = REPO / "packages/effect"
    sibling_files = sorted(
        str(p.relative_to(pkg_test_root))
        for p in EFFECT_TEST_DIR.glob("*.test.ts")
        if not p.name.startswith("__")
    )
    assert len(sibling_files) >= 10, f"unexpected sibling test count: {sibling_files}"
    r = subprocess.run(
        ["pnpm", "--filter=effect", "exec", "vitest", "run", *sibling_files,
         "--reporter=default"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=900,
        env={**os.environ, "CI": "1"},
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"sibling SchemaAST tests broke:\n{combined[-2500:]}"
