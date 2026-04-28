"""Behavioral tests for the Schema.omit + Transformation fix.

f2p tests target the bug-triggering input via tsx-executed TypeScript.
p2p tests run the existing upstream test file plus repo-level lint.
"""
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/effect")
EFFECT_PKG = REPO / "packages" / "effect"


def _run_tsx(source: str, name: str, timeout: int = 180) -> subprocess.CompletedProcess:
    """Write `source` to a scratchpad TS file and run it with `pnpm exec tsx`."""
    script = REPO / "scratchpad" / name
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(source)
    try:
        return subprocess.run(
            ["pnpm", "exec", "tsx", str(script)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        script.unlink(missing_ok=True)


# ─── fail_to_pass ─────────────────────────────────────────────────────────────


def test_omit_with_optional_default_preserves_index_signatures():
    """`Schema.omit` on a Struct combining `optionalWith({ default })` with
    `Schema.Record` must yield the same AST as omitting the same key from the
    equivalent plain Struct (i.e. a TypeLiteral with index signatures)."""
    src = textwrap.dedent('''
        import * as S from "effect/Schema"
        import { deepStrictEqual } from "node:assert/strict"

        const schema = S.Struct(
          { a: S.String, b: S.optionalWith(S.Number, { default: () => 0 }) },
          S.Record({ key: S.String, value: S.Boolean })
        )
        const plain = S.Struct(
          { a: S.String, b: S.Number },
          S.Record({ key: S.String, value: S.Boolean })
        )

        const omittedSchema = schema.pipe(S.omit("a")).ast
        const omittedPlain = plain.pipe(S.omit("a")).ast

        deepStrictEqual(omittedSchema, omittedPlain)

        if ((omittedSchema as any)._tag !== "TypeLiteral") {
          throw new Error("expected TypeLiteral, got " + (omittedSchema as any)._tag)
        }
        console.log("OK")
    ''')
    r = _run_tsx(src, "f2p_default.ts")
    assert r.returncode == 0, (
        f"omit on Struct with optionalWith({{default}}) and Record produced "
        f"a different AST than the plain-struct equivalent.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "OK" in r.stdout


def test_omit_with_optional_as_option_preserves_index_signatures():
    """Same fix must also hold for `optionalWith({ as: "Option" })`,
    which produces a Transformation AST node by the same code path."""
    src = textwrap.dedent('''
        import * as S from "effect/Schema"
        import { deepStrictEqual } from "node:assert/strict"

        const schema = S.Struct(
          { a: S.String, b: S.optionalWith(S.Number, { as: "Option" }) },
          S.Record({ key: S.String, value: S.Boolean })
        )

        const omitted = schema.pipe(S.omit("a")).ast

        if ((omitted as any)._tag !== "TypeLiteral") {
          throw new Error("expected TypeLiteral, got " + (omitted as any)._tag)
        }
        const indexSigs = (omitted as any).indexSignatures
        if (!Array.isArray(indexSigs) || indexSigs.length !== 1) {
          throw new Error("expected 1 index signature, got " + JSON.stringify(indexSigs))
        }
        console.log("OK")
    ''')
    r = _run_tsx(src, "f2p_as_option.ts")
    assert r.returncode == 0, (
        f"omit on Struct with optionalWith({{as: 'Option'}}) and Record did "
        f"not yield a TypeLiteral with index signatures.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "OK" in r.stdout


def test_omit_yields_typeliteral_with_one_index_signature():
    """The omitted AST must be a TypeLiteral carrying exactly the one
    index signature inherited from `Schema.Record(...)` — independent of
    which `optionalWith` option triggered the wrapper."""
    src = textwrap.dedent('''
        import * as S from "effect/Schema"

        function shape(s: any) {
          const ast: any = s.pipe(S.omit("a")).ast
          return {
            tag: ast._tag,
            indexCount: Array.isArray(ast.indexSignatures) ? ast.indexSignatures.length : null,
          }
        }

        const cases = [
          S.Struct(
            { a: S.String, b: S.optionalWith(S.Number, { default: () => 0 }) },
            S.Record({ key: S.String, value: S.Boolean })
          ),
          S.Struct(
            { a: S.String, b: S.optionalWith(S.Number, { as: "Option" }) },
            S.Record({ key: S.String, value: S.Number })
          ),
          S.Struct(
            { a: S.String, b: S.optionalWith(S.Number, { nullable: true }) },
            S.Record({ key: S.String, value: S.String })
          ),
        ]
        for (const c of cases) {
          const s = shape(c)
          if (s.tag !== "TypeLiteral") {
            throw new Error("expected TypeLiteral, got " + s.tag)
          }
          if (s.indexCount !== 1) {
            throw new Error("expected indexSignatures.length === 1, got " + s.indexCount)
          }
        }
        console.log("OK")
    ''')
    r = _run_tsx(src, "f2p_index_sig.ts")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert "OK" in r.stdout


# ─── pass_to_pass ─────────────────────────────────────────────────────────────


def test_existing_omit_test_file_passes():
    """The repo's own `omit.test.ts` must run cleanly under vitest."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "test/Schema/Schema/Struct/omit.test.ts"],
        cwd=EFFECT_PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"omit.test.ts did not pass.\nstdout:\n{r.stdout[-2000:]}\n"
        f"stderr:\n{r.stderr[-2000:]}"
    )


def test_pick_test_file_passes():
    """Sibling `pick.test.ts` is unaffected by the change and still passes."""
    pick_path = EFFECT_PKG / "test" / "Schema" / "Schema" / "Struct" / "pick.test.ts"
    if not pick_path.exists():
        return
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "test/Schema/Schema/Struct/pick.test.ts"],
        cwd=EFFECT_PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"pick.test.ts did not pass.\nstdout:\n{r.stdout[-2000:]}\n"
        f"stderr:\n{r.stderr[-2000:]}"
    )


def test_repo_typecheck_effect_package():
    """`tsc -b tsconfig.json` (i.e. the `pnpm check` task) for the effect
    package must succeed — the fix must be type-correct."""
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.json"],
        cwd=EFFECT_PKG,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, (
        f"Type check failed.\nstdout:\n{r.stdout[-2000:]}\n"
        f"stderr:\n{r.stderr[-2000:]}"
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

def test_ci_lint_check_for_codegen_changes():
    """pass_to_pass | CI job 'Lint' → step 'Check for codegen changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'git diff --exit-code'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for codegen changes' failed (returncode={r.returncode}):\n"
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
def test_pr_added_should_preserve_index_signatures_on_Struct_with_():
    """fail_to_pass | PR added test 'should preserve index signatures on Struct with optionalWith default' in 'packages/effect/test/Schema/Schema/Struct/omit.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/effect/test/Schema/Schema/Struct/omit.test.ts" -t "should preserve index signatures on Struct with optionalWith default" 2>&1 || npx vitest run "packages/effect/test/Schema/Schema/Struct/omit.test.ts" -t "should preserve index signatures on Struct with optionalWith default" 2>&1 || pnpm jest "packages/effect/test/Schema/Schema/Struct/omit.test.ts" -t "should preserve index signatures on Struct with optionalWith default" 2>&1 || npx jest "packages/effect/test/Schema/Schema/Struct/omit.test.ts" -t "should preserve index signatures on Struct with optionalWith default" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should preserve index signatures on Struct with optionalWith default' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
