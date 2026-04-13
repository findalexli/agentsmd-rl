"""
Task: opencode-session-token-double-count
Repo: anomalyco/opencode @ 5c15755a10fecf15630232c478302a766d295012
PR:   19758

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import re
from pathlib import Path

REPO = "/workspace/opencode"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_usage_test(ts_code: str) -> dict | list:
    """Write a temp .ts file inside the repo, run it with bun, parse JSON output."""
    tmp = Path(f"{REPO}/test_usage.ts")
    tmp.write_text(ts_code)
    r = subprocess.run(
        ["bun", "run", str(tmp)],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    output = r.stdout.decode().strip()
    for line in reversed(output.splitlines()):
        line = line.strip()
        if line.startswith("{") or line.startswith("["):
            return json.loads(line)
    raise AssertionError(
        f"No JSON output from bun script.\nstdout: {output}\nstderr: {r.stderr.decode()}"
    )


_MODEL_HELPER = '''
import { Session } from "./packages/opencode/src/session"
import type { Provider } from "./packages/opencode/src/provider/provider"

function createModel(opts: { npm?: string, cost?: any }): Provider.Model {
  return {
    id: "test-model",
    providerID: "test",
    name: "Test",
    limit: { context: 100_000, output: 32_000 },
    cost: opts.cost ?? { input: 0, output: 0, cache: { read: 0, write: 0 } },
    capabilities: {
      toolcall: true, attachment: false, reasoning: false, temperature: true,
      input: { text: true, image: false, audio: false, video: false },
      output: { text: true, image: false, audio: false, video: false },
    },
    api: { npm: opts.npm ?? "@ai-sdk/anthropic" },
    options: {},
  } as Provider.Model
}
'''


def _get_getusage_region() -> str:
    """Extract the getUsage function region from session/index.ts."""
    src = Path(f"{REPO}/packages/opencode/src/session/index.ts").read_text()
    # Match from 'export const getUsage' to the closing '  }' that is followed
    # by a blank line or another top-level export (greedy to capture the full body).
    match = re.search(
        r'export const getUsage.*?^  \}(?=\n\n|\n  export |\Z)',
        src,
        re.MULTILINE | re.DOTALL,
    )
    assert match, "Could not find getUsage function"
    return match.group(0)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """session/index.ts must parse without errors."""
    r = subprocess.run(
        ["bun", "build", "--no-bundle", "./src/session/index.ts", "--outfile", "/tmp/gate_check.js"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"session/index.ts has syntax errors:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_anthropic_input_subtracts_cache():
    """Anthropic provider: inputTokens must subtract cached tokens (varied inputs)."""
    results = _run_usage_test(_MODEL_HELPER + '''
const cases = [
  { input: 1000, output: 500, total: 1500, cached: 200 },
  { input: 5000, output: 1000, total: 6000, cached: 1500 },
  { input: 100,  output: 50,  total: 150,  cached: 0 },
]
const results = cases.map(c => {
  const r = Session.getUsage({
    model: createModel({}),
    usage: { inputTokens: c.input, outputTokens: c.output, totalTokens: c.total, cachedInputTokens: c.cached },
    metadata: { anthropic: {} },
  })
  return { input: r.tokens.input, expected: c.input - c.cached }
})
console.log(JSON.stringify(results))
''')
    for i, r in enumerate(results):
        assert r["input"] == r["expected"], (
            f"Case {i}: Anthropic input should be {r['expected']}, got {r['input']}"
        )


# [pr_diff] fail_to_pass
def test_bedrock_input_subtracts_cache():
    """Bedrock provider: inputTokens must subtract both cacheRead and cacheWrite."""
    results = _run_usage_test(_MODEL_HELPER + '''
const cases = [
  { input: 1000, output: 500, total: 1500, cacheRead: 200, cacheWrite: 300 },
  { input: 3000, output: 800, total: 3800, cacheRead: 500, cacheWrite: 100 },
  { input: 800,  output: 200, total: 1000, cacheRead: 0,   cacheWrite: 0 },
]
const results = cases.map(c => {
  const r = Session.getUsage({
    model: createModel({ npm: "@ai-sdk/amazon-bedrock" }),
    usage: { inputTokens: c.input, outputTokens: c.output, totalTokens: c.total, cachedInputTokens: c.cacheRead },
    metadata: { bedrock: { usage: { cacheWriteInputTokens: c.cacheWrite } } },
  })
  return { input: r.tokens.input, expected: c.input - c.cacheRead - c.cacheWrite }
})
console.log(JSON.stringify(results))
''')
    for i, r in enumerate(results):
        assert r["input"] == r["expected"], (
            f"Case {i}: Bedrock input should be {r['expected']}, got {r['input']}"
        )


# [pr_diff] fail_to_pass
def test_anthropic_total_uses_sdk_value():
    """Anthropic provider: total must use SDK totalTokens, not recompute from components."""
    results = _run_usage_test(_MODEL_HELPER + '''
const cases = [
  { input: 1000, output: 500, total: 1500, cached: 200, cacheWrite: 300 },
  { input: 2000, output: 800, total: 2800, cached: 400, cacheWrite: 100 },
  { input: 500,  output: 100, total: 600,  cached: 50,  cacheWrite: 0 },
]
const results = cases.map(c => {
  const r = Session.getUsage({
    model: createModel({}),
    usage: { inputTokens: c.input, outputTokens: c.output, totalTokens: c.total, cachedInputTokens: c.cached },
    metadata: { anthropic: { cacheCreationInputTokens: c.cacheWrite } },
  })
  return { total: r.tokens.total, expected: c.total }
})
console.log(JSON.stringify(results))
''')
    for i, r in enumerate(results):
        assert r["total"] == r["expected"], (
            f"Case {i}: Anthropic total should be {r['expected']} (SDK totalTokens), got {r['total']}"
        )


# [pr_diff] fail_to_pass
def test_vertex_anthropic_total_uses_sdk_value():
    """Google Vertex Anthropic: total must use SDK totalTokens."""
    results = _run_usage_test(_MODEL_HELPER + '''
const cases = [
  { input: 2000, output: 800, total: 2800, cached: 400, cacheWrite: 100 },
  { input: 1000, output: 300, total: 1300, cached: 100, cacheWrite: 50 },
  { input: 4000, output: 1500, total: 5500, cached: 1000, cacheWrite: 200 },
]
const results = cases.map(c => {
  const r = Session.getUsage({
    model: createModel({ npm: "@ai-sdk/google-vertex/anthropic" }),
    usage: { inputTokens: c.input, outputTokens: c.output, totalTokens: c.total, cachedInputTokens: c.cached },
    metadata: { anthropic: { cacheCreationInputTokens: c.cacheWrite } },
  })
  return { total: r.tokens.total, expected: c.total }
})
console.log(JSON.stringify(results))
''')
    for i, r in enumerate(results):
        assert r["total"] == r["expected"], (
            f"Case {i}: Vertex Anthropic total should be {r['expected']}, got {r['total']}"
        )


# [pr_diff] fail_to_pass
def test_bedrock_total_uses_sdk_value():
    """Bedrock provider: total must use SDK totalTokens."""
    results = _run_usage_test(_MODEL_HELPER + '''
const cases = [
  { input: 1000, output: 500, total: 1500, cacheRead: 200, cacheWrite: 300 },
  { input: 2500, output: 600, total: 3100, cacheRead: 400, cacheWrite: 150 },
  { input: 700,  output: 200, total: 900,  cacheRead: 0,   cacheWrite: 0 },
]
const results = cases.map(c => {
  const r = Session.getUsage({
    model: createModel({ npm: "@ai-sdk/amazon-bedrock" }),
    usage: { inputTokens: c.input, outputTokens: c.output, totalTokens: c.total, cachedInputTokens: c.cacheRead },
    metadata: { bedrock: { usage: { cacheWriteInputTokens: c.cacheWrite } } },
  })
  return { total: r.tokens.total, expected: c.total }
})
console.log(JSON.stringify(results))
''')
    for i, r in enumerate(results):
        assert r["total"] == r["expected"], (
            f"Case {i}: Bedrock total should be {r['expected']}, got {r['total']}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_generic_provider_cache_extraction():
    """Generic provider (OpenAI): cache read extraction and input subtraction work."""
    results = _run_usage_test(_MODEL_HELPER + '''
const cases = [
  { input: 1000, output: 500, total: 1500, cached: 200 },
  { input: 3000, output: 1000, total: 4000, cached: 800 },
  { input: 500,  output: 100, total: 600,  cached: 0 },
]
const results = cases.map(c => {
  const r = Session.getUsage({
    model: createModel({ npm: "@ai-sdk/openai" }),
    usage: { inputTokens: c.input, outputTokens: c.output, totalTokens: c.total, cachedInputTokens: c.cached },
  })
  return { input: r.tokens.input, cacheRead: r.tokens.cache.read, expInput: c.input - c.cached, expCache: c.cached }
})
console.log(JSON.stringify(results))
''')
    for i, r in enumerate(results):
        assert r["cacheRead"] == r["expCache"], f"Case {i}: Cache read should be {r['expCache']}, got {r['cacheRead']}"
        assert r["input"] == r["expInput"], f"Case {i}: Input should be {r['expInput']}, got {r['input']}"


# [repo_tests] pass_to_pass
def test_reasoning_tokens_extracted():
    """Reasoning tokens are correctly extracted from usage data."""
    results = _run_usage_test(_MODEL_HELPER + '''
const cases = [
  { input: 1000, output: 500, total: 1500, reasoning: 100 },
  { input: 2000, output: 800, total: 2800, reasoning: 350 },
  { input: 500,  output: 200, total: 700,  reasoning: 0 },
]
const results = cases.map(c => {
  const r = Session.getUsage({
    model: createModel({ npm: "@ai-sdk/openai" }),
    usage: { inputTokens: c.input, outputTokens: c.output, totalTokens: c.total, reasoningTokens: c.reasoning },
  })
  return { reasoning: r.tokens.reasoning, expected: c.reasoning }
})
console.log(JSON.stringify(results))
''')
    for i, r in enumerate(results):
        assert r["reasoning"] == r["expected"], f"Case {i}: Reasoning should be {r['expected']}, got {r['reasoning']}"


# [repo_tests] pass_to_pass
def test_zero_usage_handled():
    """Zero/undefined usage values are handled without NaN or crashes."""
    result = _run_usage_test(_MODEL_HELPER + '''
const r = Session.getUsage({
  model: createModel({ npm: "@ai-sdk/openai" }),
  usage: { inputTokens: 0, outputTokens: 0, totalTokens: 0 },
})
console.log(JSON.stringify({
  input: r.tokens.input,
  output: r.tokens.output,
  cacheRead: r.tokens.cache.read,
  costIsNaN: Number.isNaN(r.cost),
}))
''')
    assert result["input"] == 0
    assert result["output"] == 0
    assert result["cacheRead"] == 0
    assert result["costIsNaN"] is False, "Cost should not be NaN for zero usage"


# [repo_tests] pass_to_pass
def test_cost_calculation():
    """Cost calculation produces correct dollar amounts."""
    results = _run_usage_test(_MODEL_HELPER + '''
const cases = [
  {
    cost: { input: 3, output: 15, cache: { read: 0.3, write: 3.75 } },
    usage: { inputTokens: 1_000_000, outputTokens: 100_000, totalTokens: 1_100_000 },
    expected: 4.5,
  },
  {
    cost: { input: 1, output: 2, cache: { read: 0.1, write: 1 } },
    usage: { inputTokens: 500_000, outputTokens: 200_000, totalTokens: 700_000 },
    expected: 0.9,
  },
]
const results = cases.map(c => {
  const r = Session.getUsage({
    model: createModel({ npm: "@ai-sdk/openai", cost: c.cost }),
    usage: c.usage,
  })
  return { cost: r.cost, expected: c.expected }
})
console.log(JSON.stringify(results))
''')
    for i, r in enumerate(results):
        assert abs(r["cost"] - r["expected"]) < 0.001, (
            f"Case {i}: Cost should be ~{r['expected']}, got {r['cost']}"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 5c15755a10fecf15630232c478302a766d295012
def test_no_any_type_in_getusage():
    """getUsage region must not use the `any` type (AGENTS.md:13)."""
    # AST-only because: TypeScript cannot be imported in Python
    region = _get_getusage_region()
    assert not re.search(r':\s*any\b', region), (
        "getUsage contains 'any' type annotation — AGENTS.md:13 forbids it"
    )


# [agent_config] pass_to_pass — AGENTS.md:70 @ 5c15755a10fecf15630232c478302a766d295012
def test_no_let_in_getusage():
    """getUsage region must prefer const over let (AGENTS.md:70)."""
    # AST-only because: TypeScript cannot be imported in Python
    region = _get_getusage_region()
    assert not re.search(r'^\s*let\s', region, re.MULTILINE), (
        "getUsage uses 'let' — AGENTS.md:70 says prefer const"
    )


# [agent_config] pass_to_pass — AGENTS.md:84 @ 5c15755a10fecf15630232c478302a766d295012
def test_no_else_in_getusage():
    """getUsage region must not use else statements (AGENTS.md:84)."""
    # AST-only because: TypeScript cannot be imported in Python
    region = _get_getusage_region()
    assert not re.search(r'\belse\b', region), (
        "getUsage contains 'else' — AGENTS.md:84 says avoid else, prefer early returns"
    )


# [agent_config] pass_to_pass — AGENTS.md:12 @ 5c15755a10fecf15630232c478302a766d295012
def test_no_try_catch_in_getusage():
    """getUsage region must not use try/catch (AGENTS.md:12)."""
    # AST-only because: TypeScript cannot be imported in Python
    region = _get_getusage_region()
    assert not re.search(r'\btry\s*\{', region), (
        "getUsage contains try/catch — AGENTS.md:12 says avoid try/catch"
    )


# [agent_config] pass_to_pass — AGENTS.md:17 @ 5c15755a10fecf15630232c478302a766d295012
def test_no_for_loops_in_getusage():
    """getUsage region must use functional array methods, not for loops (AGENTS.md:17)."""
    # AST-only because: TypeScript cannot be imported in Python
    region = _get_getusage_region()
    assert not re.search(r'\bfor\s*\(', region), (
        "getUsage contains a for loop — AGENTS.md:17 says prefer functional array methods"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "run", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_session_tests():
    """Repo session and provider tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/session/llm.test.ts", "test/provider/transform.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Session LLM/provider transform tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_session_core_tests():
    """Repo session core tests (session.test.ts) pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/session/session.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Session core tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_provider_bedrock_tests():
    """Repo Amazon Bedrock provider tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/provider/amazon-bedrock.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Amazon Bedrock provider tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_session_system_tests():
    """Repo session system tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/session/system.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Session system tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_compaction_tests():
    """Repo session compaction tests (getUsage) pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/session/compaction.test.ts"],
        capture_output=True, text=True, timeout=180, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Session compaction tests failed:\n{r.stderr[-500:]}"
