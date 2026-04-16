# Add type generation for AI Search bindings

## Problem

Running `wrangler types` does not generate TypeScript types for AI Search bindings. When a project's `wrangler.json` config includes `ai_search_namespaces` or `ai_search` binding arrays, the generated `Env` interface omits those bindings entirely. Developers who use AI Search must manually add the type declarations, which defeats the purpose of automatic type generation.

The config parser and validator already support these binding types — they work for deployment, local dev, and CLI commands. Only the type generation step is missing.

## Expected Behavior

`wrangler types` should produce entries like:

```typescript
interface Env {
  AI_SEARCH_NS: AiSearchNamespace;   // from ai_search_namespaces config
  BLOG_SEARCH: AiSearchInstance;      // from ai_search config
}
```

Both the simple (top-level) config mode and per-environment config mode must be handled.

## Required Mappings

The type generation logic must map these config keys to TypeScript types:
- `ai_search_namespaces` → `AiSearchNamespace`
- `ai_search` → `AiSearchInstance`

## Files to Modify

- `packages/wrangler/src/type-generation/index.ts` — The type generation logic. This file contains two main functions that need to be updated:
  - `collectCoreBindings` — handles top-level binding type generation
  - `collectCoreBindingsPerEnvironment` — handles per-environment binding type generation

Both functions currently handle other binding types (like `vpc_services`, `ai`, `vectorize`, etc.) but are missing the AI Search binding types.

- `packages/wrangler/src/__tests__/type-generation.test.ts` — The test file already has mock data for `ai_search_namespaces` and `ai_search` bindings but the expected output assertions don't include the corresponding type declarations.
