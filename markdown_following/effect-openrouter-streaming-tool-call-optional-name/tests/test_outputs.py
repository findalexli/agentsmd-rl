"""Behavioral tests for effect-ts/effect#6071.

PR makes `function.name` optional in `ChatStreamingMessageToolCall` schema so
that streaming tool-call delta chunks (which omit `name` after the first SSE
chunk) decode successfully instead of raising `MalformedOutput`.
"""

import json
import os
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/effect")
SCRATCHPAD = REPO / "scratchpad"
TARGET = REPO / "packages/ai/openrouter/src/OpenRouterClient.ts"


def _write_runner(name: str, body: str) -> Path:
    SCRATCHPAD.mkdir(exist_ok=True)
    path = SCRATCHPAD / name
    path.write_text(body)
    return path


def _run_tsx(script_rel: str, timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["pnpm", "exec", "tsx", script_rel],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_streaming_tool_call_decodes_without_function_name():
    """f2p: chunk missing `function.name` (delta after first SSE) decodes."""
    body = textwrap.dedent(
        """
        import { Either, Schema } from "effect"
        import { ChatStreamingMessageToolCall } from "@effect/ai-openrouter/OpenRouterClient"

        const decode = Schema.decodeUnknownEither(ChatStreamingMessageToolCall)

        const chunk = {
          index: 0,
          type: "function",
          function: { arguments: '{"city":' }
        }

        const result = decode(chunk)
        if (Either.isLeft(result)) {
          console.error("DECODE_FAIL", String(result.left))
          process.exit(1)
        }
        const value = result.right
        if (value.index !== 0) { console.error("BAD_INDEX"); process.exit(2) }
        if (value.type !== "function") { console.error("BAD_TYPE"); process.exit(3) }
        if (value.function.arguments !== '{"city":') { console.error("BAD_ARGS"); process.exit(4) }
        console.log("OK")
        """
    ).strip() + "\n"
    _write_runner("f2p_no_name.ts", body)
    r = _run_tsx("scratchpad/f2p_no_name.ts")
    assert r.returncode == 0, (
        f"expected schema to accept tool-call chunk without `function.name` "
        f"(stdout={r.stdout!r} stderr={r.stderr[-1500:]!r})"
    )
    assert "OK" in r.stdout


def test_streaming_tool_call_preserves_name_when_present():
    """f2p: when `function.name` IS present (first chunk), it must still decode and be preserved."""
    body = textwrap.dedent(
        """
        import { Either, Schema } from "effect"
        import { ChatStreamingMessageToolCall } from "@effect/ai-openrouter/OpenRouterClient"

        const decode = Schema.decodeUnknownEither(ChatStreamingMessageToolCall)

        const chunk = {
          index: 2,
          id: "call_xyz",
          type: "function",
          function: { name: "get_weather", arguments: "" }
        }

        const result = decode(chunk)
        if (Either.isLeft(result)) {
          console.error("DECODE_FAIL", String(result.left))
          process.exit(1)
        }
        const value = result.right
        if (value.id !== "call_xyz") { console.error("BAD_ID"); process.exit(2) }
        if (value.function.name !== "get_weather") { console.error("BAD_NAME"); process.exit(3) }
        if (value.function.arguments !== "") { console.error("BAD_ARGS"); process.exit(4) }
        console.log("OK")
        """
    ).strip() + "\n"
    _write_runner("f2p_with_name.ts", body)
    r = _run_tsx("scratchpad/f2p_with_name.ts")
    assert r.returncode == 0, (
        f"chunk WITH function.name must still decode "
        f"(stdout={r.stdout!r} stderr={r.stderr[-1500:]!r})"
    )
    assert "OK" in r.stdout


def test_streaming_tool_call_arguments_still_required():
    """f2p: `function.arguments` must remain REQUIRED — only `name` was made optional."""
    body = textwrap.dedent(
        """
        import { Either, Schema } from "effect"
        import { ChatStreamingMessageToolCall } from "@effect/ai-openrouter/OpenRouterClient"

        const decode = Schema.decodeUnknownEither(ChatStreamingMessageToolCall)

        // missing `arguments` — must be rejected
        const result = decode({
          index: 0,
          type: "function",
          function: { name: "foo" }
        })
        if (Either.isRight(result)) {
          console.error("UNEXPECTED_DECODE")
          process.exit(1)
        }
        console.log("OK")
        """
    ).strip() + "\n"
    _write_runner("f2p_arguments_required.ts", body)
    r = _run_tsx("scratchpad/f2p_arguments_required.ts")
    assert r.returncode == 0, (
        f"`function.arguments` should remain required "
        f"(stdout={r.stdout!r} stderr={r.stderr[-1500:]!r})"
    )
    assert "OK" in r.stdout


def test_openrouter_typecheck_passes():
    """p2p: package's TypeScript still compiles after the fix (`pnpm check`)."""
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.json"],
        cwd=REPO / "packages/ai/openrouter",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"tsc failed:\nstdout={r.stdout[-1500:]}\nstderr={r.stderr[-1500:]}"
    )


def test_changeset_added_for_openrouter_fix():
    """agent_config: AGENTS.md mandates a changeset entry for every PR.

    Source: AGENTS.md `## Changesets` section
    (`All pull requests must include a changeset in the .changeset/ directory.`)
    Verifies a changeset file exists that bumps `@effect/ai-openrouter`.
    """
    changeset_dir = REPO / ".changeset"
    assert changeset_dir.is_dir(), "missing .changeset directory"
    candidates = [p for p in changeset_dir.glob("*.md") if p.name != "README.md"]
    matching = []
    for p in candidates:
        text = p.read_text()
        head = text.split("---", 2)
        if len(head) >= 3 and "@effect/ai-openrouter" in head[1]:
            matching.append(p)
    assert matching, (
        "no changeset entry found that bumps `@effect/ai-openrouter`. "
        "AGENTS.md requires a changeset for every PR."
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