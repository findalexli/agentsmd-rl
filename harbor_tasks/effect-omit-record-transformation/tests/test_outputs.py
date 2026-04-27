"""Verification tests for effect-omit-record-transformation task.

f2p tests (`test_omit_*`): exercise the bug behavior via vitest, expected to
fail on the base commit and pass with a correct fix.

p2p tests: run the repo's existing tests on test files that should keep
passing throughout, to detect regressions.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")
F2P_DST = REPO / "packages/effect/test/Schema/Schema/Struct/f2p_omit.test.ts"
F2P_REL = "packages/effect/test/Schema/Schema/Struct/f2p_omit.test.ts"

F2P_FIXTURE = '''import { describe, it } from "@effect/vitest"
import { deepStrictEqual, strictEqual } from "@effect/vitest/utils"
import * as S from "effect/Schema"
import * as AST from "effect/SchemaAST"

describe("f2p_omit_record_transformation", () => {
  it("default_yields_typeliteral", () => {
    const schema = S.Struct(
      { a: S.String, b: S.optionalWith(S.Number, { default: () => 0 }) },
      S.Record({ key: S.String, value: S.Boolean })
    )
    const omitted = schema.pipe(S.omit("a")).ast
    strictEqual(omitted._tag, "TypeLiteral")
    const tl = omitted as AST.TypeLiteral
    strictEqual(tl.indexSignatures.length, 1)
  })

  it("default_matches_plain", () => {
    const schema = S.Struct(
      { a: S.String, b: S.optionalWith(S.Number, { default: () => 0 }) },
      S.Record({ key: S.String, value: S.Boolean })
    )
    const plain = S.Struct(
      { a: S.String, b: S.Number },
      S.Record({ key: S.String, value: S.Boolean })
    )
    deepStrictEqual(schema.pipe(S.omit("a")).ast, plain.pipe(S.omit("a")).ast)
  })

  it("option_yields_typeliteral", () => {
    const schema = S.Struct(
      { a: S.String, b: S.optionalWith(S.Number, { as: "Option" }) },
      S.Record({ key: S.String, value: S.String })
    )
    const omitted = schema.pipe(S.omit("a")).ast
    strictEqual(omitted._tag, "TypeLiteral")
    const tl = omitted as AST.TypeLiteral
    strictEqual(tl.indexSignatures.length, 1)
  })
})
'''


def _install_f2p() -> None:
    F2P_DST.parent.mkdir(parents=True, exist_ok=True)
    F2P_DST.write_text(F2P_FIXTURE)


def _run_vitest(test_rel: str, name_filter: str | None = None,
                timeout: int = 300) -> subprocess.CompletedProcess:
    cmd = ["pnpm", "test", "run", test_rel]
    if name_filter is not None:
        cmd += ["-t", name_filter]
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)


# ---------- fail-to-pass ----------

def test_omit_optionalwith_default_yields_typeliteral():
    """omit on Struct(optionalWith default + Record) must produce TypeLiteral with index signatures."""
    _install_f2p()
    r = _run_vitest(F2P_REL, "default_yields_typeliteral")
    assert r.returncode == 0, f"vitest failed:\nSTDOUT:\n{r.stdout[-2500:]}\nSTDERR:\n{r.stderr[-1000:]}"


def test_omit_optionalwith_default_matches_plain():
    """omit on Struct(optionalWith default + Record) AST must equal plain-Number-struct equivalent."""
    _install_f2p()
    r = _run_vitest(F2P_REL, "default_matches_plain")
    assert r.returncode == 0, f"vitest failed:\nSTDOUT:\n{r.stdout[-2500:]}\nSTDERR:\n{r.stderr[-1000:]}"


def test_omit_optionalwith_option_yields_typeliteral():
    """omit on Struct(optionalWith Option + Record) must also produce TypeLiteral."""
    _install_f2p()
    r = _run_vitest(F2P_REL, "option_yields_typeliteral")
    assert r.returncode == 0, f"vitest failed:\nSTDOUT:\n{r.stdout[-2500:]}\nSTDERR:\n{r.stderr[-1000:]}"


# ---------- pass-to-pass (repo regression coverage) ----------

def test_p2p_existing_omit_test():
    """The pre-existing omit.test.ts must keep passing."""
    r = _run_vitest("packages/effect/test/Schema/Schema/Struct/omit.test.ts")
    assert r.returncode == 0, f"existing omit test broke:\nSTDOUT:\n{r.stdout[-2500:]}\nSTDERR:\n{r.stderr[-1000:]}"


def test_p2p_pick_test():
    """The sibling pick.test.ts (related code path) must keep passing."""
    r = _run_vitest("packages/effect/test/Schema/Schema/Struct/pick.test.ts")
    assert r.returncode == 0, f"pick test broke:\nSTDOUT:\n{r.stdout[-2500:]}\nSTDERR:\n{r.stderr[-1000:]}"


def test_p2p_typecheck_schemaast():
    """tsc must still typecheck the modified file (compile-time integrity)."""
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit", "-p", "packages/effect/tsconfig.src.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"tsc failed:\nSTDOUT:\n{r.stdout[-2500:]}\nSTDERR:\n{r.stderr[-2000:]}"
