# Fix GPT-5 responses API: outputType and verbosity parameter conflict

## Problem

When using the OpenAI Agents JS SDK with the Responses API model and GPT-5, you cannot simultaneously set both an `outputType` and a `verbosity` parameter. The `verbosity` setting passed through `modelSettings.providerData.text.verbosity` is silently dropped from the request sent to the OpenAI API.

This happens in **both** of these scenarios:

1. **`outputType` is `'text'` (plain text output):** The `text` configuration block containing the `verbosity` setting is discarded entirely. Only the model name and input reach the API; the verbosity instruction is lost.

2. **`outputType` is a structured schema** (e.g., `json_schema` for typed output): The `text` configuration block (with its `verbosity` setting) is dropped. The API call only receives the output format specification — not the verbosity hint that should accompany it.

Additionally, when `providerData` contains both a `text` key and other provider-specific keys like `reasoning_effort`, the raw `text` object leaks to the top level of the API request body instead of being nested correctly under the `text` parameter.

## Expected behavior

When a user configures an agent like this:

```typescript
const agent = new Agent({
  model: new OpenAIResponsesModel(client, 'gpt-5'),
  modelSettings: {
    providerData: {
      text: { verbosity: 'low' },
      reasoning_effort: 'minimal',
    },
  },
  outputType: someOutputType,  // either 'text' or a structured schema
});
```

The `responses.create()` API call should:
- Include the `verbosity` value in the `text` parameter of the request
- When `outputType` is structured, merge the verbosity with the output format specification under the `text` parameter
- Keep other `providerData` keys (like `reasoning_effort`) at the top level of the request body
- Not duplicate or leak the `text` configuration to the wrong nesting level

## Constraints

- The fix should be in the Responses model implementation within the `@openai/agents-openai` package
- The TypeScript build must continue to pass: `pnpm -F agents-openai build-check`
- Do not create changelogs, changesets, or modify example files — focus on the source code fix only

## Code Style Requirements

- Follow ESLint rules as configured in the project's `eslint.config.mjs`
- No unused imports
- Adhere to Prettier formatting defaults
- Comments must end with a period
