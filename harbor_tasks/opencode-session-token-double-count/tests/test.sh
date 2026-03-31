#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/opencode"
RESULTS_DIR="/logs/verifier"
mkdir -p "$RESULTS_DIR"

SCORE=0
TOTAL_WEIGHT=0

pass() {
  local weight=$1 desc=$2
  SCORE=$(python3 -c "print($SCORE + $weight)")
  echo "PASS ($weight): $desc"
}

fail() {
  local weight=$1 desc=$2
  echo "FAIL ($weight): $desc"
}

# ──────────────────────────────────────────────────────────────────────
# GATE: Syntax check — abort on failure
# ──────────────────────────────────────────────────────────────────────
echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): Source file must parse without errors
cd "$REPO/packages/opencode"
if ! bun build --no-bundle ./src/session/index.ts --outdir /tmp/gate_check > /dev/null 2>&1; then
  echo "GATE FAILED: session/index.ts has syntax errors"
  echo "0" > "$RESULTS_DIR/reward.txt"
  exit 0
fi
echo "GATE: syntax OK"

# ──────────────────────────────────────────────────────────────────────
# Behavioral: Fail-to-pass tests (0.80 total)
# ──────────────────────────────────────────────────────────────────────
echo ""
echo "=== Behavioral tests ==="

# Write a Bun test that exercises the actual getUsage function
cat > /tmp/test_token_usage.ts <<'TESTEOF'
import { Session } from "../../packages/opencode/src/session"
import { ModelID, ProviderID } from "../../packages/opencode/src/provider/schema"
import type { Provider } from "../../packages/opencode/src/provider/provider"

function createModel(opts: { npm?: string }): Provider.Model {
  return {
    id: "test-model",
    providerID: "test",
    name: "Test",
    limit: { context: 100_000, output: 32_000 },
    cost: { input: 0, output: 0, cache: { read: 0, write: 0 } },
    capabilities: {
      toolcall: true, attachment: false, reasoning: false, temperature: true,
      input: { text: true, image: false, audio: false, video: false },
      output: { text: true, image: false, audio: false, video: false },
    },
    api: { npm: opts.npm ?? "@ai-sdk/anthropic" },
    options: {},
  } as Provider.Model
}

// Test 1: Anthropic provider should subtract cached tokens from inputTokens
// Bug: with excludesCachedTokens=true, anthropic skips subtraction → input=1000 instead of 800
const r1 = Session.getUsage({
  model: createModel({}),
  usage: { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, cachedInputTokens: 200 },
  metadata: { anthropic: {} },
})
const t1pass = r1.tokens.input === 800
console.log(`TEST1_INPUT:${t1pass}:${r1.tokens.input}`)

// Test 2: Bedrock provider should subtract cached tokens from inputTokens
const r2 = Session.getUsage({
  model: createModel({ npm: "@ai-sdk/amazon-bedrock" }),
  usage: { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, cachedInputTokens: 200 },
  metadata: { bedrock: { usage: { cacheWriteInputTokens: 300 } } },
})
const t2pass = r2.tokens.input === 500
console.log(`TEST2_INPUT:${t2pass}:${r2.tokens.input}`)

// Test 3: Anthropic total should use totalTokens from SDK, not compute from components
// Bug: old code computes total = adjustedInput + output + cacheRead + cacheWrite = 2000
// Fixed: total = totalTokens = 1500
const r3 = Session.getUsage({
  model: createModel({}),
  usage: { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, cachedInputTokens: 200 },
  metadata: { anthropic: { cacheCreationInputTokens: 300 } },
})
const t3pass = r3.tokens.total === 1500
console.log(`TEST3_TOTAL:${t3pass}:${r3.tokens.total}`)

// Test 4: Google Vertex Anthropic total should also use totalTokens
const r4 = Session.getUsage({
  model: createModel({ npm: "@ai-sdk/google-vertex/anthropic" }),
  usage: { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, cachedInputTokens: 200 },
  metadata: { anthropic: { cacheCreationInputTokens: 300 } },
})
const t4pass = r4.tokens.total === 1500
console.log(`TEST4_TOTAL:${t4pass}:${r4.tokens.total}`)

// Test 5: Bedrock total should use totalTokens
const r5 = Session.getUsage({
  model: createModel({ npm: "@ai-sdk/amazon-bedrock" }),
  usage: { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, cachedInputTokens: 200 },
  metadata: { bedrock: { usage: { cacheWriteInputTokens: 300 } } },
})
const t5pass = r5.tokens.total === 1500
console.log(`TEST5_TOTAL:${t5pass}:${r5.tokens.total}`)
TESTEOF

cd "$REPO"
BEHAVIORAL_OUTPUT=$(bun run /tmp/test_token_usage.ts 2>&1 || true)

# [pr_diff] (0.25): Anthropic provider subtracts cached tokens from inputTokens
if echo "$BEHAVIORAL_OUTPUT" | grep -q "TEST1_INPUT:true"; then
  pass 0.25 "Anthropic: inputTokens subtracts cache"
else
  fail 0.25 "Anthropic: inputTokens should subtract cache"
fi

# [pr_diff] (0.20): Bedrock provider subtracts cached tokens from inputTokens
if echo "$BEHAVIORAL_OUTPUT" | grep -q "TEST2_INPUT:true"; then
  pass 0.20 "Bedrock: inputTokens subtracts cache (read + write)"
else
  fail 0.20 "Bedrock: inputTokens should subtract cache"
fi

# [pr_diff] (0.15): Anthropic total uses SDK totalTokens
if echo "$BEHAVIORAL_OUTPUT" | grep -q "TEST3_TOTAL:true"; then
  pass 0.15 "Anthropic: total uses SDK totalTokens"
else
  fail 0.15 "Anthropic: total should use SDK totalTokens, not recompute"
fi

# [pr_diff] (0.10): Google Vertex Anthropic total uses SDK totalTokens
if echo "$BEHAVIORAL_OUTPUT" | grep -q "TEST4_TOTAL:true"; then
  pass 0.10 "Google Vertex Anthropic: total uses SDK totalTokens"
else
  fail 0.10 "Google Vertex Anthropic: total should use SDK totalTokens"
fi

# [pr_diff] (0.10): Bedrock total uses SDK totalTokens
if echo "$BEHAVIORAL_OUTPUT" | grep -q "TEST5_TOTAL:true"; then
  pass 0.10 "Bedrock: total uses SDK totalTokens"
else
  fail 0.10 "Bedrock: total should use SDK totalTokens"
fi

# ──────────────────────────────────────────────────────────────────────
# Pass-to-pass: Existing behavior must not break (0.15)
# ──────────────────────────────────────────────────────────────────────
echo ""
echo "=== Pass-to-pass tests ==="

# Run the existing tests that should still pass (non-provider-specific getUsage tests)
cat > /tmp/test_p2p.ts <<'P2PEOF'
import { Session } from "../../packages/opencode/src/session"
import type { Provider } from "../../packages/opencode/src/provider/provider"

function createModel(opts?: { cost?: Provider.Model["cost"] }): Provider.Model {
  return {
    id: "test-model", providerID: "test", name: "Test",
    limit: { context: 100_000, output: 32_000 },
    cost: opts?.cost ?? { input: 0, output: 0, cache: { read: 0, write: 0 } },
    capabilities: {
      toolcall: true, attachment: false, reasoning: false, temperature: true,
      input: { text: true, image: false, audio: false, video: false },
      output: { text: true, image: false, audio: false, video: false },
    },
    api: { npm: "@ai-sdk/openai" },
    options: {},
  } as Provider.Model
}

// P2P 1: Generic provider cache read extraction still works
const r1 = Session.getUsage({
  model: createModel(),
  usage: { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, cachedInputTokens: 200 },
})
console.log(`P2P_CACHE_READ:${r1.tokens.cache.read === 200 && r1.tokens.input === 800}`)

// P2P 2: Reasoning tokens still extracted
const r2 = Session.getUsage({
  model: createModel(),
  usage: { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, reasoningTokens: 100 },
})
console.log(`P2P_REASONING:${r2.tokens.reasoning === 100}`)

// P2P 3: Undefined optional values handled gracefully
const r3 = Session.getUsage({
  model: createModel(),
  usage: { inputTokens: 0, outputTokens: 0, totalTokens: 0 },
})
const ok = r3.tokens.input === 0 && r3.tokens.output === 0 && r3.tokens.cache.read === 0 && !Number.isNaN(r3.cost)
console.log(`P2P_ZEROES:${ok}`)

// P2P 4: Cost calculation still correct
const r4 = Session.getUsage({
  model: createModel({ cost: { input: 3, output: 15, cache: { read: 0.3, write: 3.75 } } }),
  usage: { inputTokens: 1_000_000, outputTokens: 100_000, totalTokens: 1_100_000 },
})
const costOk = Math.abs(r4.cost - 4.5) < 0.001
console.log(`P2P_COST:${costOk}:${r4.cost}`)
P2PEOF

cd "$REPO"
P2P_OUTPUT=$(bun run /tmp/test_p2p.ts 2>&1 || true)

# [repo_tests] (0.05): Generic provider cache extraction
if echo "$P2P_OUTPUT" | grep -q "P2P_CACHE_READ:true"; then
  pass 0.05 "P2P: generic provider cache read extraction"
else
  fail 0.05 "P2P: generic provider cache read extraction broken"
fi

# [repo_tests] (0.05): Reasoning tokens extraction
if echo "$P2P_OUTPUT" | grep -q "P2P_REASONING:true"; then
  pass 0.05 "P2P: reasoning tokens extraction"
else
  fail 0.05 "P2P: reasoning tokens extraction broken"
fi

# [repo_tests] (0.03): Graceful handling of zeroes/undefined
if echo "$P2P_OUTPUT" | grep -q "P2P_ZEROES:true"; then
  pass 0.03 "P2P: zero/undefined values handled gracefully"
else
  fail 0.03 "P2P: zero/undefined value handling broken"
fi

# [repo_tests] (0.02): Cost calculation correctness
if echo "$P2P_OUTPUT" | grep -q "P2P_COST:true"; then
  pass 0.02 "P2P: cost calculation correct"
else
  fail 0.02 "P2P: cost calculation broken"
fi

# ──────────────────────────────────────────────────────────────────────
# Config-derived checks (0.05)
# ──────────────────────────────────────────────────────────────────────
echo ""
echo "=== Config-derived checks ==="

FILE="$REPO/packages/opencode/src/session/index.ts"

# [agent_config] (0.03): "Avoid using the `any` type" — AGENTS.md:19
# Check the getUsage function area for 'any' type annotations
GETUSAGE_REGION=$(sed -n '/export const getUsage/,/^  }/p' "$FILE" 2>/dev/null || true)
if echo "$GETUSAGE_REGION" | grep -qP ':\s*any\b'; then
  fail 0.03 "Config: no 'any' type in getUsage"
else
  pass 0.03 "Config: no 'any' type in getUsage"
fi

# [agent_config] (0.02): "Prefer `const` over `let`" — AGENTS.md:54
if echo "$GETUSAGE_REGION" | grep -qP '^\s*let\s'; then
  fail 0.02 "Config: prefer const over let in getUsage"
else
  pass 0.02 "Config: no let in getUsage"
fi

# ──────────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────────
echo ""
echo "=== Final Score ==="
echo "Score: $SCORE"
echo "$SCORE" > "$RESULTS_DIR/reward.txt"

# Generate reward.json
python3 -c "
import json
score = float('$SCORE')
# Approximate breakdown
behavioral = min(0.80, score)
regression = min(0.15, max(0, score - 0.80))
config = min(0.05, max(0, score - 0.95))
json.dump({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
}, open('$RESULTS_DIR/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
