"""Behavioral tests for effect-ts/effect#6117.

The bug: in `OpenRouterLanguageModel.makeStreamResponse`, when OpenRouter
ends a streamed response with a "usage-only" terminal chunk (`choices: []`
+ a populated `usage`), the function rejected the chunk as malformed and
the whole stream errored at the very end -- even though the model had
already streamed all of its output. Real, valid model responses were
being lost.

Each scenario below is fed through the public streaming API by way of a
mock `OpenRouterClient` Layer; the resulting stream is consumed and the
collected parts (or terminal error) are emitted as JSON for inspection.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")
PKG = REPO / "packages/ai/openrouter"
RUNNER_DST = PKG / "streaming_runner.mts"

# tsx is installed globally; use it from PATH rather than the workspace
# node_modules (which may not include it when --filter is used at install time).
TSX = "tsx"

# TS test harness. Lives in this file (rather than a sibling .mts) so the
# tests/ directory stays clean. Materialized into the package directory at
# test time so tsx can resolve `@effect/ai-openrouter` etc. via pnpm's
# `workspace:^` links.
RUNNER_TS = r"""
import * as OpenRouterLanguageModel from "@effect/ai-openrouter/OpenRouterLanguageModel"
import { OpenRouterClient } from "@effect/ai-openrouter/OpenRouterClient"
import * as LanguageModel from "@effect/ai/LanguageModel"
import * as Effect from "effect/Effect"
import * as Layer from "effect/Layer"
import * as Stream from "effect/Stream"
import * as Chunk from "effect/Chunk"
import * as Cause from "effect/Cause"
import * as DateTime from "effect/DateTime"

const mkChunk = (overrides: any) => ({
  id: "test-id",
  model: "openai/gpt-4",
  provider: "openrouter",
  created: DateTime.unsafeMake(0),
  choices: [],
  ...overrides
})

const scenarios: Record<string, Array<any>> = {
  "text-then-usage": [
    mkChunk({ choices: [{ index: 0, delta: { content: "Hello" } }] }),
    mkChunk({ choices: [{ index: 0, delta: { content: " world" }, finish_reason: "stop" }] }),
    mkChunk({
      choices: [],
      usage: { prompt_tokens: 13, completion_tokens: 16, total_tokens: 29 }
    })
  ],
  "usage-only-terminal": [
    mkChunk({
      choices: [],
      usage: { prompt_tokens: 7, completion_tokens: 11, total_tokens: 18 }
    })
  ],
  "empty-chunk": [
    mkChunk({ choices: [] })
  ]
}

const scenario = process.argv[2]
const chunks = scenarios[scenario]
if (!chunks) {
  console.log(JSON.stringify({ ok: false, error: `unknown scenario ${scenario}`, parts: null }))
  process.exit(2)
}

const mockClientService = {
  client: {} as any,
  createChatCompletion: () => Effect.die("not used"),
  createChatCompletionStream: () => Stream.fromIterable(chunks as any)
}

const ClientLayer = Layer.succeed(OpenRouterClient, mockClientService as any)
const ModelLayer = OpenRouterLanguageModel.layer({ model: "openai/gpt-4" }).pipe(
  Layer.provide(ClientLayer)
)

const program: Effect.Effect<{ ok: boolean; error: string | null; parts: Array<any> | null }> =
  LanguageModel.streamText({ prompt: "hi" }).pipe(
    Stream.runCollect,
    Effect.map((c) => ({ ok: true, error: null, parts: Chunk.toReadonlyArray(c) as Array<any> })),
    Effect.catchAllCause((c) =>
      Effect.succeed({ ok: false, error: Cause.pretty(c), parts: null })
    ),
    Effect.provide(ModelLayer)
  ) as any

const result = await Effect.runPromise(program)
const replacer = (_k: string, v: any) =>
  v && typeof v === "object" && v._tag === "Some" ? v.value : v
console.log(JSON.stringify(result, replacer))
"""


def _ensure_runner_installed() -> None:
    current = RUNNER_DST.read_text() if RUNNER_DST.exists() else ""
    if current != RUNNER_TS:
        RUNNER_DST.write_text(RUNNER_TS)


def _run_scenario(name: str) -> dict:
    _ensure_runner_installed()
    result = subprocess.run(
        [TSX, str(RUNNER_DST), name],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "NODE_OPTIONS": "--no-warnings"},
    )
    last_line = ""
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            last_line = line
    assert last_line, (
        "no JSON envelope on stdout. "
        f"stdout={result.stdout!r} stderr={result.stderr[-800:]!r}"
    )
    return json.loads(last_line)


def _find_part(parts, ptype):
    return [p for p in parts if p.get("type") == ptype]


def test_usage_only_terminal_chunk_succeeds():
    """A stream whose only chunk is a usage-only terminal must succeed."""
    out = _run_scenario("usage-only-terminal")
    assert out["ok"], (
        "stream errored on a usage-only terminal chunk; the adapter must "
        f"treat such chunks as a valid stream end. error={out['error']}"
    )
    assert out["parts"] is not None
    finish = _find_part(out["parts"], "finish")
    assert len(finish) == 1, (
        f"expected exactly one finish part, got {[p['type'] for p in out['parts']]}"
    )
    usage = finish[0].get("usage") or {}
    assert usage.get("inputTokens") == 7
    assert usage.get("outputTokens") == 11
    assert usage.get("totalTokens") == 18


def test_text_stream_with_usage_terminal_succeeds():
    """Text deltas before a usage-only terminal must all surface."""
    out = _run_scenario("text-then-usage")
    assert out["ok"], (
        "stream errored on a usage-only terminal chunk after text; "
        f"prior content must still be delivered. error={out['error']}"
    )
    parts = out["parts"]
    deltas = [p.get("delta") for p in _find_part(parts, "text-delta")]
    assert "Hello" in deltas and " world" in deltas, (
        f"text deltas should include both 'Hello' and ' world'; got {deltas}"
    )
    finish = _find_part(parts, "finish")
    assert len(finish) == 1, "exactly one finish part expected"
    usage = finish[0].get("usage") or {}
    assert usage.get("totalTokens") == 29, (
        f"expected total_tokens=29 carried into finish.usage; got {usage}"
    )


def test_empty_terminal_chunk_still_errors():
    """A chunk with neither choices nor usage must still raise MalformedOutput.

    Guards against a trivial 'swallow all errors' fix.
    """
    out = _run_scenario("empty-chunk")
    assert not out["ok"], (
        "an empty chunk (no choices, no usage) must still be rejected. "
        f"parts={out['parts']}"
    )
    assert "MalformedOutput" in (out["error"] or ""), (
        f"expected MalformedOutput, got {out['error']!r}"
    )


def test_changeset_file_added():
    """AGENTS.md: 'All pull requests must include a changeset in .changeset/'.

    Verify a new .md changeset was added beyond the 6 that exist at the base
    commit.
    """
    files = sorted(p.name for p in (REPO / ".changeset").glob("*.md"))
    assert len(files) >= 7, (
        "expected a new changeset file in .changeset/ (AGENTS.md mandates one "
        f"for every PR); only found {files}"
    )


def test_repo_lint_passes():
    """Repo's eslint passes on the openrouter package src."""
    result = subprocess.run(
        ["pnpm", "exec", "eslint", "src"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"eslint failed:\n{result.stdout[-1500:]}\n{result.stderr[-1500:]}"
    )


def test_repo_typecheck_passes():
    """Repo's `pnpm check` (tsc -b) passes on the openrouter package."""
    result = subprocess.run(
        ["pnpm", "check"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"pnpm check failed:\n{result.stdout[-1500:]}\n{result.stderr[-1500:]}"
    )


def test_ci_lint_pnpm():
    """pass_to_pass | CI job 'Lint' step: pnpm circular"""
    result = subprocess.run(
        ["pnpm", "circular"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"pnpm circular failed (returncode={result.returncode}):\n"
        f"stdout: {result.stdout[-1500:]}\nstderr: {result.stderr[-1500:]}")


def test_ci_lint_pnpm_2():
    """pass_to_pass | CI job 'Lint' step: pnpm lint"""
    result = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"pnpm lint failed (returncode={result.returncode}):\n"
        f"stdout: {result.stdout[-1500:]}\nstderr: {result.stderr[-1500:]}")


def test_ci_lint_pnpm_3():
    """pass_to_pass | CI job 'Lint' step: pnpm codegen"""
    result = subprocess.run(
        ["pnpm", "codegen"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"pnpm codegen failed (returncode={result.returncode}):\n"
        f"stdout: {result.stdout[-1500:]}\nstderr: {result.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
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
