#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

FILE="packages/opencode/src/session/index.ts"
TEST_FILE="packages/opencode/test/session/compaction.test.ts"

# Idempotency check
if ! grep -q 'excludesCachedTokens' "$FILE" 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

python3 << 'PYEOF'
import re

# Fix 1: Read and modify the main source file
with open('packages/opencode/src/session/index.ts', 'r') as f:
    content = f.read()

# Remove the iife import
content = re.sub(r'^import { iife } from "@/util/iife"\n', '', content, flags=re.MULTILINE)

# Replace the old provider-specific logic with the new simplified logic
old_logic = """    // OpenRouter provides inputTokens as the total count of input tokens (including cached).
    // AFAIK other providers (OpenRouter/OpenAI/Gemini etc.) do it the same way e.g. vercel/ai#8794 (comment)
    // Anthropic does it differently though - inputTokens doesn't include cached tokens.
    // It looks like OpenCode's cost calculation assumes all providers return inputTokens the same way Anthropic does (I'm guessing getUsage logic was originally implemented with anthropic), so it's causing incorrect cost calculation for OpenRouter and others.
    const excludesCachedTokens = !!(input.metadata?.["anthropic"] || input.metadata?.["bedrock"])
    const adjustedInputTokens = safe(
      excludesCachedTokens ? inputTokens : inputTokens - cacheReadInputTokens - cacheWriteInputTokens,
    )"""

new_logic = """    // AI SDK v6 normalized inputTokens to include cached tokens across all providers
    // (including Anthropic/Bedrock which previously excluded them). Always subtract cache
    // tokens to get the non-cached input count for separate cost calculation.
    const adjustedInputTokens = safe(inputTokens - cacheReadInputTokens - cacheWriteInputTokens)"""

content = content.replace(old_logic, new_logic)

# Replace the old iife total calculation
old_total = """    const total = iife(() => {
      // Anthropic doesn't provide total_tokens, also ai sdk will vastly undercount if we
      // don't compute from components
      if (
        input.model.api.npm === "@ai-sdk/anthropic" ||
        input.model.api.npm === "@ai-sdk/amazon-bedrock" ||
        input.model.api.npm === "@ai-sdk/google-vertex/anthropic"
      ) {
        return adjustedInputTokens + outputTokens + cacheReadInputTokens + cacheWriteInputTokens
      }
      return input.usage.totalTokens
    })"""

new_total = '    const total = input.usage.totalTokens'

content = content.replace(old_total, new_total)

with open('packages/opencode/src/session/index.ts', 'w') as f:
    f.write(content)

print('Main source file patched successfully.')

# Fix 2: Read and modify the test file
with open('packages/opencode/test/session/compaction.test.ts', 'r') as f:
    test_content = f.read()

# Fix test name
test_content = test_content.replace(
    'test("does not subtract cached tokens for anthropic provider"',
    'test("subtracts cached tokens for anthropic provider"'
)

# Find and fix the anthropic test - change input from 1000 to 800
# Look for the pattern in the specific test
test_content = test_content.replace(
    'test("subtracts cached tokens for anthropic provider", () => {\n    const model = createModel({ context: 100_000, output: 32_000 })\n    const result = Session.getUsage({',
    'test("subtracts cached tokens for anthropic provider", () => {\n    const model = createModel({ context: 100_000, output: 32_000 })\n    // AI SDK v6 normalizes inputTokens to include cached tokens for all providers\n    const result = Session.getUsage({'
)

# Change the expected value from 1000 to 800 in this specific test
# We need to be careful to only change the one in this specific test
test_content = test_content.replace(
    'expect(result.tokens.input).toBe(1000)\n    expect(result.tokens.cache.read).toBe(200)\n  })',
    'expect(result.tokens.input).toBe(800)\n    expect(result.tokens.cache.read).toBe(200)\n  })',
    1  # Only replace the first occurrence (the anthropic test)
)

# Fix the test.each block for Bedrock
bedrock_old = """if (npm === "@ai-sdk/amazon-bedrock") {
        const result = Session.getUsage({
          model,
          usage,
          metadata: {
            bedrock: {
              usage: {
                cacheWriteInputTokens: 300,
              },
            },
          },
        })

        expect(result.tokens.input).toBe(1000)
        expect(result.tokens.cache.read).toBe(200)
        expect(result.tokens.cache.write).toBe(300)
        expect(result.tokens.total).toBe(2000)
        return
      }"""

bedrock_new = """if (npm === "@ai-sdk/amazon-bedrock") {
        // AI SDK v6: inputTokens includes cached tokens for all providers
        const result = Session.getUsage({
          model,
          usage,
          metadata: {
            bedrock: {
              usage: {
                cacheWriteInputTokens: 300,
              },
            },
          },
        })

        // inputTokens (1000) includes cache, so adjusted = 1000 - 200 - 300 = 500
        expect(result.tokens.input).toBe(500)
        expect(result.tokens.cache.read).toBe(200)
        expect(result.tokens.cache.write).toBe(300)
        // total = adjusted (500) + output (500) + cacheRead (200) + cacheWrite (300)
        expect(result.tokens.total).toBe(1500)
        return
      }"""

test_content = test_content.replace(bedrock_old, bedrock_new)

# Fix the test.each block for Anthropic (the else branch)
anthropic_old = """// These providers typically report total as input + output only,
        // excluding cache read/write.
        totalTokens: 1500,
        cachedInputTokens: 200,
      }
      if (npm === "@ai-sdk/amazon-bedrock") {"""

anthropic_new = """totalTokens: 1500,
        cachedInputTokens: 200,
      }
      if (npm === "@ai-sdk/amazon-bedrock") {"""

test_content = test_content.replace(anthropic_old, anthropic_new)

# Fix the Anthropic assertions
anthropic_assert_old = """      const result = Session.getUsage({
        model,
        usage,
        metadata: {
          anthropic: {
            cacheCreationInputTokens: 300,
          },
        },
      })

      expect(result.tokens.input).toBe(1000)
      expect(result.tokens.cache.read).toBe(200)
      expect(result.tokens.cache.write).toBe(300)
      expect(result.tokens.total).toBe(2000)"""

anthropic_assert_new = """      // AI SDK v6: inputTokens includes cached tokens for all providers
      const result = Session.getUsage({
        model,
        usage,
        metadata: {
          anthropic: {
            cacheCreationInputTokens: 300,
          },
        },
      })

      // inputTokens (1000) includes cache, so adjusted = 1000 - 200 - 300 = 500
      expect(result.tokens.input).toBe(500)
      expect(result.tokens.cache.read).toBe(200)
      expect(result.tokens.cache.write).toBe(300)
      // total = adjusted (500) + output (500) + cacheRead (200) + cacheWrite (300)
      expect(result.tokens.total).toBe(1500)"""

test_content = test_content.replace(anthropic_assert_old, anthropic_assert_new)

with open('packages/opencode/test/session/compaction.test.ts', 'w') as f:
    f.write(test_content)

print('Test file patched successfully.')
PYEOF

echo "All patches applied successfully."
