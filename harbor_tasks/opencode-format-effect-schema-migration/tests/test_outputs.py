"""Behavioural tests for opencode#23744 — Effect Schema migration of MessageV2.Format."""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode/packages/opencode"

_PROBE_MIGRATION = """\
import { describe, expect, test } from "bun:test"
import { MessageV2 } from "../src/session/message-v2"

describe("effect-schema-migration-leaves", () => {
  test("OutputFormatText is a Schema.Class with constructible instances", () => {
    expect(typeof (MessageV2 as any).OutputFormatText).toBe("function")
    const inst: any = new (MessageV2 as any).OutputFormatText({ type: "text" })
    expect(inst.type).toBe("text")
  })

  test("OutputFormatJsonSchema is a Schema.Class with constructible instances", () => {
    expect(typeof (MessageV2 as any).OutputFormatJsonSchema).toBe("function")
    const inst: any = new (MessageV2 as any).OutputFormatJsonSchema({
      type: "json_schema",
      schema: { type: "object" },
      retryCount: 3,
    })
    expect(inst.type).toBe("json_schema")
    expect(inst.retryCount).toBe(3)
  })

  test("OutputFormatText exposes a Zod-compatible .zod accessor", () => {
    const z = (MessageV2 as any).OutputFormatText.zod
    expect(z).toBeDefined()
    expect(typeof z.safeParse).toBe("function")
    const ok = z.safeParse({ type: "text" })
    expect(ok.success).toBe(true)
    const bad = z.safeParse({ type: "json_schema" })
    expect(bad.success).toBe(false)
  })

  test("OutputFormatJsonSchema .zod parses with retryCount default of 2", () => {
    const z = (MessageV2 as any).OutputFormatJsonSchema.zod
    const ok = z.safeParse({ type: "json_schema", schema: { type: "object" } })
    expect(ok.success).toBe(true)
    if (ok.success) expect(ok.data.retryCount).toBe(2)

    const custom = z.safeParse({ type: "json_schema", schema: { type: "object" }, retryCount: 7 })
    expect(custom.success).toBe(true)
    if (custom.success) expect(custom.data.retryCount).toBe(7)
  })

  test("OutputFormatJsonSchema .zod rejects negative retryCount and missing schema", () => {
    const z = (MessageV2 as any).OutputFormatJsonSchema.zod
    expect(z.safeParse({ type: "json_schema", schema: {}, retryCount: -1 }).success).toBe(false)
    expect(z.safeParse({ type: "json_schema" }).success).toBe(false)
  })
})
"""

_PROBE_FORMAT = """\
import { describe, expect, test } from "bun:test"
import { MessageV2 } from "../src/session/message-v2"
import { SessionPrompt } from "../src/session/prompt"

describe("format-migration-regression", () => {
  test("Format exposes a Zod-compatible .zod accessor that handles the union", () => {
    const z = (MessageV2 as any).Format.zod
    expect(z).toBeDefined()
    expect(typeof z.safeParse).toBe("function")

    expect(z.safeParse({ type: "text" }).success).toBe(true)
    expect(z.safeParse({ type: "json_schema", schema: { type: "object" } }).success).toBe(true)
    expect(z.safeParse({ type: "invalid" }).success).toBe(false)
  })

  test("Format is no longer a direct Zod schema (no .safeParse on Format)", () => {
    expect((MessageV2 as any).Format.safeParse).toBeUndefined()
  })

  test("PromptInput accepts format via the migrated .zod accessor", () => {
    const ok = (SessionPrompt as any).PromptInput.safeParse({
      sessionID: "ses_01HXYZ0000000000000000000000",
      parts: [],
      format: { type: "text" },
    })
    expect(ok.success).toBe(true)

    const okJson = (SessionPrompt as any).PromptInput.safeParse({
      sessionID: "ses_01HXYZ0000000000000000000000",
      parts: [],
      format: { type: "json_schema", schema: { type: "object" } },
    })
    expect(okJson.success).toBe(true)

    const badFormat = (SessionPrompt as any).PromptInput.safeParse({
      sessionID: "ses_01HXYZ0000000000000000000000",
      parts: [],
      format: { type: "bogus" },
    })
    expect(badFormat.success).toBe(false)
  })
})
"""


def _run_bun_test(test_path: str, timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bun", "test", test_path, "--timeout", "30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _write_probe(dst_filename: str, content: str) -> None:
    probe_path = Path(REPO) / "test" / dst_filename
    probe_path.write_text(content)


def _cleanup_probe(dst_filename: str) -> None:
    probe_path = Path(REPO) / "test" / dst_filename
    if probe_path.exists():
        probe_path.unlink()


def test_effect_schema_migration_leaves():
    """f2p: OutputFormatText and OutputFormatJsonSchema are Schema.Class instances with .zod accessors."""
    _write_probe("_probe_migration.test.ts", _PROBE_MIGRATION)
    try:
        r = _run_bun_test("test/_probe_migration.test.ts")
        assert r.returncode == 0, (
            f"Effect Schema leaf migration probe failed (exit={r.returncode}):\n"
            f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}"
        )
    finally:
        _cleanup_probe("_probe_migration.test.ts")


def test_format_migration_regression():
    """f2p: Format is a Schema.Union with .zod, Format.safeParse is removed, PromptInput accepts format."""
    _write_probe("_probe_format.test.ts", _PROBE_FORMAT)
    try:
        r = _run_bun_test("test/_probe_format.test.ts")
        assert r.returncode == 0, (
            f"Format migration probe failed (exit={r.returncode}):\n"
            f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}"
        )
    finally:
        _cleanup_probe("_probe_format.test.ts")


def test_structured_output_test():
    """p2p: upstream test/session/structured-output.test.ts (22 tests)."""
    r = _run_bun_test("test/session/structured-output.test.ts")
    assert r.returncode == 0, (
        f"structured-output.test.ts failed:\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}"
    )


def test_message_v2_test():
    """p2p: upstream test/session/message-v2.test.ts (24 tests)."""
    r = _run_bun_test("test/session/message-v2.test.ts")
    assert r.returncode == 0, (
        f"message-v2.test.ts failed:\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")