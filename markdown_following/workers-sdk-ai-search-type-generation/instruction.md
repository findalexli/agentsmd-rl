# Add type generation for AI Search bindings

## Problem

Running `wrangler types` does not generate TypeScript types for AI Search bindings. When a project's `wrangler.json` config includes `ai_search_namespaces` or `ai_search` binding arrays, the generated `Env` interface omits those bindings entirely. Developers who use AI Search must manually add the type declarations, which defeats the purpose of automatic type generation.

The config parser and validator already support these binding types — they work for deployment, local dev, and CLI commands. Only the type generation step is missing. The existing type generation pipeline already handles other binding types such as `vpc_services` (→ `Fetcher`), `ai` (→ `Ai`), `rate_limits` (→ `RateLimit`), `vectorize` (→ `VectorizeIndex`), and `send_email` (→ `SendEmail`). These existing mappings must continue to work.

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

## Code Style Requirements

- **oxlint**: Run `npx oxlint --deny-warnings --type-aware` from the wrangler package directory. All lint checks must pass.
- **oxfmt**: Run `npx oxfmt --check src scripts bin` from the wrangler package directory. All formatting checks must pass.

The existing test suite for type generation must still pass, and the updated type generation output must include
the new AI Search binding types alongside the existing ones.
