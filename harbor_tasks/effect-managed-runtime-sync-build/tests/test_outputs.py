"""Behavioral tests for effect-ts/effect PR #6079: build ManagedRuntime synchronously.

Each `def test_*` maps 1:1 to a check id in eval_manifest.yaml.
"""
import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")
PKG = REPO / "packages" / "effect"

# Verifier-owned test injected at runtime; written by the helper below.
INJECTED_TEST_PATH = PKG / "test" / "_pr6079_sync_verifier.test.ts"

INJECTED_TEST_TS = '''import { describe, it } from "@effect/vitest"
import { strictEqual } from "@effect/vitest/utils"
import { Context, Effect, Layer, ManagedRuntime } from "effect"

describe("__pr6079_sync_build_verifier", () => {
  it("runSync works immediately after runFork on Layer.empty", () => {
    const runtime = ManagedRuntime.make(Layer.empty)
    runtime.runFork(Effect.void)
    runtime.runSync(Effect.void)
  })

  it("runSync returns the value immediately after runFork on Layer.succeed", () => {
    const tag = Context.GenericTag<string>("__pr6079_value")
    const runtime = ManagedRuntime.make(Layer.succeed(tag, "hello"))
    runtime.runFork(Effect.void)
    const result = runtime.runSync(tag)
    strictEqual(result, "hello")
  })

  it("ManagedRuntime built from a sync layer caches its runtime synchronously after runFork", () => {
    const tag = Context.GenericTag<number>("__pr6079_number")
    const layer = Layer.succeed(tag, 42)
    const managed = ManagedRuntime.make(layer) as unknown as { cachedRuntime: unknown }
    ;(managed as unknown as { runFork: (e: unknown) => void }).runFork(Effect.void)
    if (managed.cachedRuntime === undefined) {
      throw new Error("cachedRuntime should be defined synchronously after runFork on a sync layer")
    }
  })
})
'''


def _ensure_injected_test() -> None:
    INJECTED_TEST_PATH.write_text(INJECTED_TEST_TS)


def _vitest(test_rel_path: str, timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["pnpm", "--silent", "vitest", "run", "--reporter=basic", test_rel_path],
        cwd=str(PKG),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _format_failure(label: str, r: subprocess.CompletedProcess) -> str:
    return (
        f"{label} failed (exit={r.returncode})\n"
        f"--- STDOUT (tail) ---\n{r.stdout[-3000:]}\n"
        f"--- STDERR (tail) ---\n{r.stderr[-1500:]}\n"
    )


def test_runtime_builds_synchronously_after_runfork():
    """fail_to_pass: runSync must succeed immediately after runFork when the layer is synchronously buildable."""
    _ensure_injected_test()
    r = _vitest("test/_pr6079_sync_verifier.test.ts", timeout=240)
    assert r.returncode == 0, _format_failure("sync-build verifier", r)


def test_managed_runtime_existing_suite_passes():
    """pass_to_pass: existing ManagedRuntime test suite still passes."""
    r = _vitest("test/ManagedRuntime.test.ts", timeout=240)
    assert r.returncode == 0, _format_failure("ManagedRuntime suite", r)


def test_changeset_added_for_effect_package():
    """agent_config: AGENTS.md mandates a .changeset/*.md entry for every PR (source: AGENTS.md L37-39)."""
    cs_dir = REPO / ".changeset"
    md_files = [p for p in cs_dir.glob("*.md") if p.name.lower() != "readme.md"]
    matching = []
    for p in md_files:
        text = p.read_text()
        if '"effect"' in text and (": patch" in text or ": minor" in text or ": major" in text):
            matching.append(p.name)
    assert matching, (
        "AGENTS.md requires a .changeset/<name>.md file with effect package version-bump frontmatter "
        f'(e.g. \'"effect": patch\'). Found markdown files: {[p.name for p in md_files]!r}'
    )
