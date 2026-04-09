# Task: Fix Inline Backticks in Tool Instructions

## Problem

The system message strings that provide tool usage instructions to AI models contain raw triple-backtick sequences (\`\`\`) in the prose text. This causes ambiguous fence nesting in the system prompt, making it difficult for models to reliably distinguish actual tool-call code fences from instructional text.

## Affected File

`core/tools/systemMessageTools/toolCodeblocks/index.ts`

## What Needs to Change

In the `SystemMessageToolCodeblocksFramework` class:

1. **systemMessagePrefix**: The text currently mentions "a tool code block (\`\`\`tool)" - change this to reference the format without using literal backticks, e.g., "the tool code block format shown below"

2. **systemMessageSuffix**: Two rules need updating:
   - Rule 1: Change "output a \`\`\`tool code block" to "output a tool code block"
   - Rule 4: Change "the closing \`\`\`" to "the closing fence"

## Constraints

- The actual code examples (like `exampleDynamicToolDefinition`, `exampleDynamicToolCall`) and the parsing patterns (`acceptedToolCallStarts`) should NOT be modified - they legitimately need the backticks for functionality
- The TypeScript file must still compile without errors
- The changes should only affect the prose/instructional text

## Expected Outcome

After the fix, the system message strings should describe the tool code block format without using literal triple-backtick sequences in the descriptive prose, eliminating the fence nesting ambiguity while preserving all functional code examples.
