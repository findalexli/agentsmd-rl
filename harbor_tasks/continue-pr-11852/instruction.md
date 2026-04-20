# Fix MCP Tool Argument Type Coercion Bug

## Context

The Continue codebase has an MCP (Model Context Protocol) tool calling system in `core/tools/`. When calling MCP tools, arguments are processed through `JSON.parse()` which deeply parses all values - including strings that should remain as strings.

## The Bug

When an MCP tool's input schema defines a parameter as `type: "string"`, but the argument value contains valid JSON (e.g., file content for a `.json` file), `JSON.parse()` converts it to a JavaScript object instead of keeping it as a string.

**Example symptom:**
- Tool schema: `{ "type": "object", "properties": { "content": { "type": "string" } } }`
- Input args: `{ "content": "{\"key\": \"value\"}" }` (a JSON string)
- After `JSON.parse()`: `{ "content": {"key": "value"} }` (an object, not a string!)
- The MCP tool receives `{"key": "value"}` (object) instead of `"{\"key\": \"value\"}"` (string)

This causes MCP tools to receive wrong types - objects/arrays where strings are expected.

## Required Implementation

The solution requires:
- A function named `coerceArgsToSchema` exported from `core/tools/parseArgs.ts`
- This function is called in `core/tools/callTool.ts` using the tool's schema parameters accessed via `extras.tool?.function?.parameters`

## Expected Behavior

When calling MCP tools, argument values must match the types specified in the tool's input schema. String-typed parameters should receive string values, not parsed JSON objects.

## Verification

The fix is correct when:
- Object-typed values in string fields get stringified: `{content: {key: "value"}}` → `{content: "{\"key\":\"value\"}"}`
- Array-typed values in string fields get stringified: `{content: ["a", "b"]}` → `{content: "[\"a\",\"b\"]"}`
- String values remain unchanged: `{content: "hello"}` → `{content: "hello"}`
- Numbers remain as numbers (not stringified): `{content: 42}` → `{content: 42}`
- Booleans remain as booleans: `{content: true}` → `{content: true}`
- Original args object is not mutated
- TypeScript compiles without errors
- Existing vitest tests pass

## Testing

Run `npm run vitest -- parseArgs.vitest.ts --run` in the `core/` directory to verify the fix works correctly.