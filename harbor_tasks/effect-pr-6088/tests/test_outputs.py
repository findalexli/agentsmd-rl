import subprocess
import os
import tempfile

REPO = "/workspace/effect"


def test_omit_preserves_index_signatures():
    """
    Schema.omit on Struct with optionalWith({default}) and Record must produce
    a TypeLiteral with index signatures. At base commit, getIndexSignatures()
    lacks the Transformation case, so omit returns a structurally wrong schema.
    """
    test_code = """
import { describe, it } from "@effect/vitest";
import { deepStrictEqual } from "@effect/vitest/utils";
import * as S from "effect/Schema";

describe("omit preserves index signatures", () => {
  it("with optionalWith default (omit b)", () => {
    const schema = S.Struct(
      { a: S.String, b: S.optionalWith(S.Number, { default: () => 0 }) },
      S.Record({ key: S.String, value: S.Boolean })
    );
    const plain = S.Struct(
      { a: S.String, b: S.Number },
      S.Record({ key: S.String, value: S.Boolean })
    );
    deepStrictEqual(schema.pipe(S.omit("b")).ast, plain.pipe(S.omit("b")).ast);
  });

  it("with optionalWith default (omit a, string default)", () => {
    const schema = S.Struct(
      { x: S.Number, y: S.optionalWith(S.String, { default: () => "hello" }) },
      S.Record({ key: S.String, value: S.Number })
    );
    const plain = S.Struct(
      { x: S.Number, y: S.String },
      S.Record({ key: S.String, value: S.Number })
    );
    deepStrictEqual(schema.pipe(S.omit("x")).ast, plain.pipe(S.omit("x")).ast);
  });
});
"""

    test_path = os.path.join(
        REPO, "packages/effect/test/Schema/Schema/Struct/omit_index_signatures_fix.test.ts"
    )
    with open(test_path, "w") as f:
        f.write(test_code)

    try:
        r = subprocess.run(
            ["pnpm", "vitest", "run", "packages/effect/test/Schema/Schema/Struct/omit_index_signatures_fix.test.ts"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert r.returncode == 0, (
            f"Vitest failed (rc={r.returncode}):\n"
            f"STDOUT:\n{r.stdout[-600:]}\n"
            f"STDERR:\n{r.stderr[-600:]}"
        )
    finally:
        if os.path.exists(test_path):
            os.unlink(test_path)


def test_omit_with_as_option_preserves_index_signatures():
    """
    Schema.omit on Struct with optionalWith({as: "Option"}) and Record must
    produce a TypeLiteral with index signatures. At base commit,
    getIndexSignatures() lacks the Transformation case, so omit returns a
    structurally wrong schema.
    """
    test_code = """
import { describe, it } from "@effect/vitest";
import { deepStrictEqual } from "@effect/vitest/utils";
import * as S from "effect/Schema";

describe("omit preserves index signatures (as: Option)", () => {
  it("with optionalWith as Option (omit b)", () => {
    const schema = S.Struct(
      { a: S.optionalWith(S.NumberFromString, { as: "Option" }), b: S.String },
      S.Record({ key: S.String, value: S.Boolean })
    );
    const plain = S.Struct(
      { a: S.NumberFromString, b: S.String },
      S.Record({ key: S.String, value: S.Boolean })
    );
    deepStrictEqual(schema.pipe(S.omit("b")).ast, plain.pipe(S.omit("b")).ast);
  });
});
"""

    test_path = os.path.join(
        REPO, "packages/effect/test/Schema/Schema/Struct/omit_index_signatures_as_option_fix.test.ts"
    )
    with open(test_path, "w") as f:
        f.write(test_code)

    try:
        r = subprocess.run(
            ["pnpm", "vitest", "run", "packages/effect/test/Schema/Schema/Struct/omit_index_signatures_as_option_fix.test.ts"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert r.returncode == 0, (
            f"Vitest failed (rc={r.returncode}):\n"
            f"STDOUT:\n{r.stdout[-600:]}\n"
            f"STDERR:\n{r.stderr[-600:]}"
        )
    finally:
        if os.path.exists(test_path):
            os.unlink(test_path)


def test_existing_omit_test_passes():
    """Existing omit.test.ts test passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "packages/effect/test/Schema/Schema/Struct/omit.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Existing omit test failed (rc={r.returncode}):\n"
        f"STDOUT:\n{r.stdout[-500:]}\n"
        f"STDERR:\n{r.stderr[-500:]}"
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