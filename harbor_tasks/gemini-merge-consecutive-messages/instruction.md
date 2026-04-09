# Fix Gemini API Consecutive Same-Role Message Error

## Problem

The Gemini API is returning 400 errors in multi-tool-call conversations. When Continue converts chat messages to Gemini format, tool responses are mapped to `"user"` role with `functionResponse` parts. Multiple consecutive tool responses create consecutive `"user"` messages, violating Gemini's strict role alternation requirement.

The specific errors are:
1. "Please ensure that function call turn comes immediately after a user turn or after a function response turn."
2. "Please ensure that the number of function response parts is equal to the number of function call parts of the function call turn."

## Your Task

Add a post-processing step that **merges consecutive same-role messages** by combining their `parts` arrays. This should:

1. Work for both `user` role messages (tool responses) and `model` role messages (assistant responses)
2. Be applied in both `core/llm/llms/Gemini.ts` and `packages/openai-adapters/src/apis/Gemini.ts`
3. Preserve all content while ensuring strict user/model alternation

## Key Files

- `core/llm/llms/Gemini.ts` - Core Gemini LLM implementation
- `core/llm/llms/gemini-types.ts` - Core Gemini type definitions
- `packages/openai-adapters/src/apis/Gemini.ts` - OpenAI adapter Gemini API
- `packages/openai-adapters/src/util/gemini-types.ts` - Adapter Gemini type definitions

## Implementation Hints

- Create a `mergeConsecutiveGeminiMessages` function that takes an array of `GeminiChatContent` and returns a merged array
- The function should iterate through messages, merging consecutive ones with the same role by concatenating their `parts` arrays
- Apply this function after message conversion but before sending to the API
- Consider edge cases: empty arrays, single messages, already-alternating messages

## Testing

The repository has existing test infrastructure. If you add tests, you should run them to verify they pass.

## Expected Behavior

Before fix (causes API error):
```json
[
  { "role": "user", "parts": [...] },
  { "role": "model", "parts": [...] },
  { "role": "user", "parts": [functionResponse1] },  // ← consecutive user
  { "role": "user", "parts": [functionResponse2] }   // ← consecutive user (ERROR!)
]
```

After fix (valid for API):
```json
[
  { "role": "user", "parts": [...] },
  { "role": "model", "parts": [...] },
  { "role": "user", "parts": [functionResponse1, functionResponse2] }  // ← merged
]
```
