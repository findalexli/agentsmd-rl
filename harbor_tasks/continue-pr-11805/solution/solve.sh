#!/bin/bash
set -e

cd /workspace/continue

# ============================================
# 1. Add mergeConsecutiveGeminiMessages to core/llm/llms/gemini-types.ts
# ============================================
if ! grep -q "mergeConsecutiveGeminiMessages" core/llm/llms/gemini-types.ts; then
  cat >> core/llm/llms/gemini-types.ts << 'ENDOFFILE'

// Gemini requires strict user/model role alternation.
export function mergeConsecutiveGeminiMessages(
  contents: GeminiChatContent[],
): GeminiChatContent[] {
  if (contents.length === 0) {
    return contents;
  }

  const merged: GeminiChatContent[] = [contents[0]];

  for (let i = 1; i < contents.length; i++) {
    const current = contents[i];
    const previous = merged[merged.length - 1];

    if (current.role === previous.role) {
      previous.parts = [...previous.parts, ...current.parts];
    } else {
      merged.push(current);
    }
  }

  return merged;
}
ENDOFFILE
  echo "Added mergeConsecutiveGeminiMessages to core/llm/llms/gemini-types.ts"
fi

# ============================================
# 2. Update core/llm/llms/Gemini.ts
# ============================================
if ! grep -q "mergeConsecutiveGeminiMessages" core/llm/llms/Gemini.ts; then
  # Add import after the last import line from gemini-types
  sed -i '/from ".\/gemini-types";/a\import { mergeConsecutiveGeminiMessages } from "./gemini-types";' core/llm/llms/Gemini.ts

  # Add merge call before "return body;" in prepareBody
  sed -i '/return body;$/i\    body.contents = mergeConsecutiveGeminiMessages(body.contents);' core/llm/llms/Gemini.ts

  echo "Updated core/llm/llms/Gemini.ts"
fi

# ============================================
# 3. Add mergeConsecutiveGeminiMessages to packages/openai-adapters/src/util/gemini-types.ts
# ============================================
if ! grep -q "mergeConsecutiveGeminiMessages" packages/openai-adapters/src/util/gemini-types.ts; then
  cat >> packages/openai-adapters/src/util/gemini-types.ts << 'ENDOFFILE'

// Gemini requires strict user/model role alternation.
export function mergeConsecutiveGeminiMessages(
  contents: GeminiChatContent[],
): GeminiChatContent[] {
  if (contents.length === 0) {
    return contents;
  }

  const merged: GeminiChatContent[] = [contents[0]];

  for (let i = 1; i < contents.length; i++) {
    const current = contents[i];
    const previous = merged[merged.length - 1];

    if (current.role === previous.role) {
      previous.parts = [...previous.parts, ...current.parts];
    } else {
      merged.push(current);
    }
  }

  return merged;
}
ENDOFFILE
  echo "Added mergeConsecutiveGeminiMessages to packages/openai-adapters/src/util/gemini-types.ts"
fi

# ============================================
# 4. Update packages/openai-adapters/src/apis/Gemini.ts
# ============================================
if ! grep -q "mergeConsecutiveGeminiMessages" packages/openai-adapters/src/apis/Gemini.ts; then
  # Add import after the existing gemini-types import
  sed -i '/from "..\/util\/gemini-types.js";$/a\import { mergeConsecutiveGeminiMessages } from "..\/util\/gemini-types.js";' packages/openai-adapters/src/apis/Gemini.ts

  # Use python to make the multi-line changes
  python3 << 'PYTHON_SCRIPT'
import re

filepath = '/workspace/continue/packages/openai-adapters/src/apis/Gemini.ts'

with open(filepath, 'r') as f:
    content = f.read()

# The filter line is:
#       .filter((c) => c !== null);
# We need to change it to add const mergedContents after it, and then
# change the "contents," line to "contents: mergedContents,"

# First, find the filter line and add the const after it
# The line before filter ends with });  so we match .filter((c) => c !== null);
old_filter = r'\.filter\(\(c\) => c !== null\);'
new_filter = '''.filter((c) => c !== null);

    const mergedContents = mergeConsecutiveGeminiMessages(contents as any);'''

if 'const mergedContents' not in content:
    content = re.sub(old_filter, new_filter, content)
    print("Added const mergedContents after filter line")

# Now change "contents," to "contents: mergedContents," in finalBody
# Find the pattern: generationConfig,\n      contents,
if 'contents: mergedContents' not in content:
    content = re.sub(
        r'generationConfig,\n\s+contents,',
        'generationConfig,\n      contents: mergedContents,',
        content
    )
    print("Changed contents, to contents: mergedContents, in finalBody")

with open(filepath, 'w') as f:
    f.write(content)

print("Done updating Gemini.ts")
PYTHON_SCRIPT

  echo "Updated packages/openai-adapters/src/apis/Gemini.ts"
fi

# Verify the patch was applied
if grep -q "mergeConsecutiveGeminiMessages" core/llm/llms/gemini-types.ts && \
   grep -q "mergeConsecutiveGeminiMessages" packages/openai-adapters/src/apis/Gemini.ts && \
   grep -q "mergedContents" packages/openai-adapters/src/apis/Gemini.ts; then
  echo "Fix applied successfully"
else
  echo "ERROR: Fix may not have been applied correctly"
  exit 1
fi