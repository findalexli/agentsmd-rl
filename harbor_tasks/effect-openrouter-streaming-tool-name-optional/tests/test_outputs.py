import json
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")
PKG = REPO / "packages/ai/openrouter"
TEST_DIR = PKG / "test"
TEST_FILE = TEST_DIR / "harbor-streaming-tool-call.test.ts"
RESULTS_FILE = Path("/tmp/vitest-results.json")

VITEST_TEST = r"""
import { assert, describe, it } from "@effect/vitest"
import { Effect, Schema } from "effect"
import * as OpenRouterClient from "@effect/ai-openrouter/OpenRouterClient"

describe("ChatStreamingMessageToolCall", () => {
  it.effect("decodes_chunk_without_function_name", () =>
    Effect.gen(function*() {
      const result = yield* Schema.decodeUnknown(
        OpenRouterClient.ChatStreamingMessageToolCall
      )({
        index: 0,
        type: "function",
        function: { arguments: "{\"a\":1}" }
      })
      assert.strictEqual(result.index, 0)
      assert.strictEqual(result.type, "function")
      assert.strictEqual(result.function.arguments, "{\"a\":1}")
    })
  )

  it.effect("decodes_continuation_chunk_with_only_arguments", () =>
    Effect.gen(function*() {
      const result = yield* Schema.decodeUnknown(
        OpenRouterClient.ChatStreamingMessageToolCall
      )({
        index: 7,
        type: "function",
        function: { arguments: "\"city\"" }
      })
      assert.strictEqual(result.index, 7)
      assert.strictEqual(result.function.arguments, "\"city\"")
    })
  )

  it.effect("decodes_initial_chunk_with_id_and_name", () =>
    Effect.gen(function*() {
      const result = yield* Schema.decodeUnknown(
        OpenRouterClient.ChatStreamingMessageToolCall
      )({
        index: 0,
        id: "call_abc123",
        type: "function",
        function: { name: "get_weather", arguments: "" }
      })
      assert.strictEqual(result.id, "call_abc123")
      assert.strictEqual(result.function.name, "get_weather")
      assert.strictEqual(result.function.arguments, "")
    })
  )

  it.effect("decodes_chunk_with_null_name", () =>
    Effect.gen(function*() {
      const result = yield* Schema.decodeUnknown(
        OpenRouterClient.ChatStreamingMessageToolCall
      )({
        index: 1,
        id: null,
        type: "function",
        function: { name: null, arguments: "abc" }
      })
      assert.strictEqual(result.function.arguments, "abc")
    })
  )

  it.effect("rejects_chunk_missing_arguments", () =>
    Effect.gen(function*() {
      const exit = yield* Effect.exit(
        Schema.decodeUnknown(OpenRouterClient.ChatStreamingMessageToolCall)({
          index: 0,
          type: "function",
          function: { name: "x" }
        })
      )
      assert.isTrue(exit._tag === "Failure", "expected decode to fail")
    })
  )
})
"""


def _ensure_test_file_written():
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    if not TEST_FILE.exists() or TEST_FILE.read_text() != VITEST_TEST:
        TEST_FILE.write_text(VITEST_TEST)


_results_cache = None


def _run_vitest():
    global _results_cache
    if _results_cache is not None:
        return _results_cache
    _ensure_test_file_written()
    if RESULTS_FILE.exists():
        RESULTS_FILE.unlink()
    cmd = [
        "pnpm",
        "exec",
        "vitest",
        "run",
        "test/harbor-streaming-tool-call.test.ts",
        "--reporter=json",
        f"--outputFile={RESULTS_FILE}",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(PKG),
        capture_output=True,
        text=True,
        timeout=300,
    )
    if not RESULTS_FILE.exists():
        raise AssertionError(
            "vitest did not produce a results file.\n"
            f"stdout:\n{proc.stdout[-2000:]}\n\nstderr:\n{proc.stderr[-2000:]}"
        )
    _results_cache = json.loads(RESULTS_FILE.read_text())
    return _results_cache


def _assertion_status(name_substr: str) -> str:
    results = _run_vitest()
    for f in results.get("testResults", []):
        for a in f.get("assertionResults", []):
            full = a.get("fullName") or a.get("title") or ""
            if name_substr in full:
                return a.get("status", "unknown")
    raise AssertionError(
        f"vitest assertion '{name_substr}' not found.\nResults: "
        f"{json.dumps(results, indent=2)[:2000]}"
    )


def test_decodes_chunk_without_function_name():
    """f2p: Continuation tool-call chunks (no function.name) must decode."""
    status = _assertion_status("decodes_chunk_without_function_name")
    assert status == "passed", f"vitest reported status={status}"


def test_decodes_continuation_chunk_with_only_arguments():
    """f2p: Argument-delta chunks with only function.arguments must decode."""
    status = _assertion_status("decodes_continuation_chunk_with_only_arguments")
    assert status == "passed", f"vitest reported status={status}"


def test_decodes_chunk_with_null_name():
    """f2p: function.name explicitly null must decode (nullable: true)."""
    status = _assertion_status("decodes_chunk_with_null_name")
    assert status == "passed", f"vitest reported status={status}"


def test_decodes_initial_chunk_with_id_and_name():
    """p2p: Initial chunks with id+name still decode (must not regress)."""
    status = _assertion_status("decodes_initial_chunk_with_id_and_name")
    assert status == "passed", f"vitest reported status={status}"


def test_rejects_chunk_missing_arguments():
    """p2p: function.arguments remains required (no over-loosening)."""
    status = _assertion_status("rejects_chunk_missing_arguments")
    assert status == "passed", f"vitest reported status={status}"


def test_pnpm_check_openrouter():
    """p2p: openrouter package type-checks (`pnpm check`)."""
    proc = subprocess.run(
        ["pnpm", "check"],
        cwd=str(PKG),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode == 0, (
        f"`pnpm check` failed in openrouter package.\n"
        f"stdout:\n{proc.stdout[-1500:]}\n\nstderr:\n{proc.stderr[-1500:]}"
    )


def test_eslint_openrouter_src():
    """p2p: openrouter src lints clean (eslint)."""
    proc = subprocess.run(
        ["pnpm", "exec", "eslint", "packages/ai/openrouter/src"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert proc.returncode == 0, (
        f"eslint failed on openrouter src.\n"
        f"stdout:\n{proc.stdout[-1500:]}\n\nstderr:\n{proc.stderr[-1500:]}"
    )
