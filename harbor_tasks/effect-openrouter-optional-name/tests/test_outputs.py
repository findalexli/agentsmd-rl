"""Tests for effect-ts/effect#6071 — optional function.name in ChatStreamingMessageToolCall."""

import subprocess
import os

REPO = "/workspace/effect"


def run(cmd, **kwargs):
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("timeout", 120)
    return subprocess.run(cmd, **kwargs)


def _write_test_file():
    """Write the schema test into the workspace scratchpad so tsx can resolve
    workspace-linked packages (@effect/ai-openrouter, effect/Schema, etc.)."""
    scratchpad = os.path.join(REPO, "scratchpad")
    os.makedirs(scratchpad, exist_ok=True)
    test_path = os.path.join(scratchpad, "test_schema.ts")
    with open(test_path, "w") as f:
        f.write("""\
/**
 * Test: ChatStreamingMessageToolCall schema MUST accept chunks without
 * `function.name`. The OpenAI streaming spec sends name only on the first
 * chunk; subsequent chunks omit it.
 */
import { OpenRouterClient } from "@effect/ai-openrouter"
import * as Schema from "effect/Schema"

const { ChatStreamingMessageToolCall } = OpenRouterClient

const chunk = {
  index: 0,
  id: null,
  type: "function" as const,
  function: {
    arguments: '{"location": "San Francisco"}'
  }
}

Schema.decodeUnknownSync(ChatStreamingMessageToolCall)(chunk)
console.log("OK")
""")
    return test_path


def _write_test_file_index_1():
    """Write a second variant: chunk with index=1 and non-null id, also missing
    function.name — simulates a later chunk in a multi-chunk stream."""
    scratchpad = os.path.join(REPO, "scratchpad")
    os.makedirs(scratchpad, exist_ok=True)
    test_path = os.path.join(scratchpad, "test_schema_index_1.ts")
    with open(test_path, "w") as f:
        f.write("""\
/**
 * Test: Second chunk (index=1) without function.name MUST also decode.
 * Uses Schema.decodeEither to exercise the Either-returning API path.
 */
import { OpenRouterClient } from "@effect/ai-openrouter"
import * as Schema from "effect/Schema"
import * as Either from "effect/Either"

const { ChatStreamingMessageToolCall } = OpenRouterClient

const chunk = {
  index: 1,
  id: "call_abc123",
  type: "function" as const,
  function: {
    arguments: '{"result": 42}'
  }
}

const result = Schema.decodeEither(ChatStreamingMessageToolCall)(chunk)

if (Either.isRight(result)) {
  console.log("OK")
} else {
  console.error("FAIL: decodeEither returned Left for valid chunk without function.name")
  process.exit(1)
}
""")
    return test_path


# -- fail_to_pass tests -----------------------------------------------------

def test_missing_name_decode():
    """Chunks without function.name MUST decode (decodeUnknownSync path)."""
    test_path = _write_test_file()
    r = run(["tsx", test_path], cwd=REPO)
    assert r.returncode == 0, (
        f"Decode failed (exit {r.returncode}). Chunks without function.name "
        f"should be accepted.\nSTDERR:\n{r.stderr[-800:]}"
    )


def test_missing_name_index_1():
    """Chunk at index=1 without function.name MUST decode (decodeEither path)."""
    test_path = _write_test_file_index_1()
    r = run(["tsx", test_path], cwd=REPO)
    assert r.returncode == 0, (
        f"Decode failed (exit {r.returncode}). Chunk at index=1 without "
        f"function.name should be accepted.\nSTDERR:\n{r.stderr[-800:]}"
    )


# -- pass_to_pass tests -----------------------------------------------------

def test_repo_typecheck():
    """TypeScript type-checking passes on the openrouter package."""
    r = run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.json"],
        cwd=os.path.join(REPO, "packages/ai/openrouter"),
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Type check failed (exit {r.returncode}).\nSTDERR:\n{r.stderr[-800:]}"
    )


def test_ci_lint_pnpm():
    """pass_to_pass | CI job 'Lint' — pnpm circular (dependency cycle check)."""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm circular'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"pnpm circular failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_lint_pnpm_2():
    """pass_to_pass | CI job 'Lint' — pnpm lint (code style)."""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"pnpm lint failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_lint_pnpm_3():
    """pass_to_pass | CI job 'Lint' — pnpm codegen (code generation check)."""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm codegen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"pnpm codegen failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
