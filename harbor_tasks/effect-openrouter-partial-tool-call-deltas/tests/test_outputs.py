"""Tests for effect-ts/effect#6131: allow partial tool_call deltas in OpenRouter streaming."""
import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/effect"
PKG = f"{REPO}/packages/ai/openrouter"


def _run_ts(script: str, timeout: int = 120) -> dict:
    """Execute a TypeScript snippet via tsx and parse trailing JSON line.

    The snippet must call `out({...})` exactly once with a JSON-serialisable
    summary; we extract it from stdout's last non-empty line so other logging
    is harmless.
    """
    helper = textwrap.dedent(
        """
        const out = (obj) => process.stdout.write(JSON.stringify(obj) + "\\n");
        """
    )
    full = helper + "\n" + script
    script_path = Path("/tmp/_tc_check.ts")
    script_path.write_text(full)
    r = subprocess.run(
        ["pnpm", "exec", "tsx", str(script_path)],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    assert r.returncode == 0, (
        f"tsx exited {r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr[-2000:]}"
    )
    last = [ln for ln in r.stdout.splitlines() if ln.strip().startswith("{")]
    assert last, f"no JSON line in stdout:\n{r.stdout}"
    return json.loads(last[-1])


def _decode_many(inputs: list[dict]) -> list[dict]:
    """Decode each input via ChatStreamingMessageToolCall; return list of {ok, error}."""
    inputs_lit = json.dumps(inputs)
    script = f"""
        import * as Schema from "effect/Schema"
        import {{ OpenRouterClient }} from "@effect/ai-openrouter"
        import {{ Either }} from "effect"

        const decode = Schema.decodeUnknownEither(OpenRouterClient.ChatStreamingMessageToolCall)
        const inputs = {inputs_lit} as const
        const results = inputs.map((inp) => {{
          const r = decode(inp)
          return Either.isRight(r)
            ? {{ ok: true }}
            : {{ ok: false, error: String(r.left).slice(0, 400) }}
        }})
        out({{ results }})
    """
    return _run_ts(script)["results"]


# --- fail-to-pass: behaviour that must work after the fix ---

def test_decodes_chunk_missing_type_and_arguments():
    """Initial streaming chunk lacks `type` and `function.arguments`."""
    [r] = _decode_many([{"index": 0, "id": "call_1", "function": {"name": "lookup"}}])
    assert r["ok"], f"decode rejected partial chunk: {r.get('error')}"


def test_decodes_chunk_missing_only_type():
    """Chunk has `function.arguments` but omits `type`."""
    [r] = _decode_many(
        [{"index": 0, "id": "call_1", "function": {"name": "lookup", "arguments": "{\"q"}}]
    )
    assert r["ok"], f"decode rejected chunk without type: {r.get('error')}"


def test_decodes_chunk_missing_only_arguments():
    """Chunk has `type=function` but omits `function.arguments` (continuation delta)."""
    [r] = _decode_many(
        [{"index": 1, "type": "function", "function": {"name": "lookup"}}]
    )
    assert r["ok"], f"decode rejected chunk without arguments: {r.get('error')}"


def test_decodes_continuation_delta_with_only_arg_fragment():
    """Mid-stream delta carrying only an arguments fragment under `function`."""
    [r] = _decode_many([{"index": 2, "function": {"arguments": "uery\":1}"}}])
    assert r["ok"], f"decode rejected continuation delta: {r.get('error')}"


def test_decodes_full_streaming_sequence():
    """A typical OpenRouter streaming sequence: header chunk + arg fragments."""
    sequence = [
        {"index": 0, "id": "call_xyz", "type": "function", "function": {"name": "search"}},
        {"index": 0, "function": {"arguments": "{\"q"}},
        {"index": 0, "function": {"arguments": "uery\""}},
        {"index": 0, "function": {"arguments": ":\"hi\"}"}},
    ]
    results = _decode_many(sequence)
    for i, r in enumerate(results):
        assert r["ok"], f"chunk #{i} rejected: {r.get('error')}"


# --- pass-to-pass: pre-existing contracts that must stay intact ---

def test_full_valid_tool_call_still_decodes():
    """Sanity: a fully-formed tool call (the legacy shape) still passes decoding."""
    [r] = _decode_many(
        [
            {
                "index": 0,
                "id": "call_1",
                "type": "function",
                "function": {"name": "lookup", "arguments": "{\"q\":\"x\"}"},
            }
        ]
    )
    assert r["ok"], f"valid tool call decode regressed: {r.get('error')}"


def test_invalid_type_literal_still_rejected():
    """`type` must remain constrained to the literal `function` when present."""
    [r] = _decode_many(
        [{"index": 0, "type": "not_a_function", "function": {"name": "x"}}]
    )
    assert not r["ok"], "invalid `type` literal was accepted; constraint regressed"


def test_index_remains_required():
    """`index` is the only always-required field; it must still be enforced."""
    [r] = _decode_many([{"type": "function", "function": {"name": "x"}}])
    assert not r["ok"], "missing `index` was accepted; required-field guard regressed"


def test_index_must_be_number():
    """`index` must remain typed as number (not string)."""
    [r] = _decode_many([{"index": "0", "function": {"name": "x"}}])
    assert not r["ok"], "string `index` was accepted; type-narrowing regressed"


def test_typescript_compiles():
    """Repo's own TypeScript build of the openrouter package must keep type-checking."""
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.src.json"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"tsc failed:\nstdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_package_vitest():
    """pass_to_pass | vitest run scoped to the openrouter package."""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm exec vitest run --passWithNoTests --project @effect/ai-openrouter'],
        cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"vitest failed (returncode={r.returncode}):\n"
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