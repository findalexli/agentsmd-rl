import subprocess
import os
import sys

REPO = "/workspace/effect"

TEST_FILE_CONTENT = """\
import { Rpc } from "@effect/rpc"
import { Cause, Exit, Schema } from "effect"
import { assert, describe, it } from "@effect/vitest"

describe("defect schema", () => {
  it("exitSchema uses custom defectSchema when provided", () => {
    const rpc = Rpc.make("testCustomDefect", {
      success: Schema.String
    })

    // Simulate what the formal defect option enables:
    // override the defectSchema to use Schema.Unknown so full defect
    // objects survive encode/decode round-trips
    Object.assign(rpc, { defectSchema: Schema.Unknown })

    const schema = Rpc.exitSchema(rpc)
    const encode = Schema.encodeSync(schema)
    const decode = Schema.decodeSync(schema)

    const error = {
      message: "boom",
      stack: "Error: boom\\n  at foo.ts:1",
      code: 42
    }
    const exit = Exit.die(error)

    const roundTripped = decode(encode(exit))

    assert.isTrue(Exit.isFailure(roundTripped))
    const defect = Cause.squash((roundTripped as Exit.Failure<any, any>).cause)

    // With Schema.Unknown the full object survives; with Schema.Defect
    // (the base-commit hardcode) it's truncated to { message: "boom" }
    assert.deepStrictEqual(defect, error)
  })
})
"""


def test_exit_schema_custom_defect():
    """exitSchema uses the RPC's defectSchema instead of hardcoded Schema.Defect.

    On the base commit, exitSchema hardcodes Schema.Defect for the defect
    portion of the Exit schema. After the fix, it reads rpc.defectSchema
    which defaults to Schema.Defect but can be overridden per-RPC.
    """
    test_dir = os.path.join(REPO, "packages", "rpc", "test")
    os.makedirs(test_dir, exist_ok=True)
    test_path = os.path.join(test_dir, "defect_schema.test.ts")

    with open(test_path, "w") as f:
        f.write(TEST_FILE_CONTENT)

    try:
        r = subprocess.run(
            ["pnpm", "exec", "vitest", "run", "packages/rpc/test/defect_schema.test.ts"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )
        # Print output for debugging
        if r.returncode != 0:
            print(f"VITEST FAILED:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
        assert r.returncode == 0, f"exitSchema defect schema test failed with code {r.returncode}"
    finally:
        # Clean up
        if os.path.exists(test_path):
            os.remove(test_path)


def test_rpc_existing_tests():
    """Existing RPC vitest tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "packages/rpc/test/Rpc.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r.returncode != 0:
        print(f"RPC vitest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    assert r.returncode == 0, f"Existing RPC tests failed with code {r.returncode}"

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