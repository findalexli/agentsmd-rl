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

## Files to Look At

- `packages/wrangler/src/type-generation/index.ts` — The type generation logic. The file contains two main functions:
  - `collectCoreBindings` — registers each binding using an `addBinding` helper function. For example, `vpc_services` bindings call `addBinding(binding, "Fetcher", "vpc_services", envName)` to map the binding to its TypeScript type.
  - `collectCoreBindingsPerEnvironment` — registers each binding by pushing objects to a `bindings` array with `{ bindingCategory, name, type }` properties. For example, `vpc_services` calls `bindings.push({ bindingCategory: "vpc_services", name: binding, type: "Fetcher" })`.

  Both functions currently lack handling for AI Search config keys. They need to handle:
  - `ai_search_namespaces` config → type `"AiSearchNamespace"`
  - `ai_search` config → type `"AiSearchInstance"`

- `packages/wrangler/src/__tests__/type-generation.test.ts` — The test file already has mock data for `ai_search_namespaces` and `ai_search` bindings but the expected output doesn't include them.
