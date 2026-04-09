# Refactor: Rework User Memory Search

## Problem

The current user memory search system has limitations that prevent efficient and flexible memory retrieval:

1. **Single query string limitation**: The `searchUserMemory` tool only accepts a single `query` string, preventing multi-intent searches
2. **No structured filtering**: Missing support for filtering by time ranges, categories, tags, labels, relationships, status, or memory types
3. **No taxonomy discovery**: There's no way to discover available categories, tags, and other taxonomy options before searching
4. **Missing identities in search results**: The search doesn't return identity memories
5. **Incomplete time-based search**: No support for calendar-friendly time selectors like "last month" or "yesterday"

## Expected Behavior

After the refactor:

1. **`searchUserMemory` accepts multiple queries**: Change from `query: string` to `queries: string[]` to support multiple search intents
2. **Add structured filtering parameters**:
   - `layers`: Filter by memory layers (activity, context, experience, identity, preference)
   - `categories`: Filter by memory categories
   - `tags`: Filter by tags
   - `labels`: Filter by labels
   - `relationships`: Filter identity relationships
   - `status`: Filter by status values
   - `types`: Filter by memory types
   - `timeRange`: Exact time range filtering
   - `timeIntent`: Calendar-friendly time selectors (today, yesterday, lastWeek, etc.)
   - `topK`: Per-layer result limits (now includes `identities`)
3. **Add `queryTaxonomyOptions` tool**: New API to discover available taxonomy options (categories, tags, labels, statuses, roles, relationships, types)
4. **Include identities in results**: Search results should now include `identities` array alongside activities, contexts, experiences, and preferences
5. **Updated search metadata**: Results should include `meta` with ranking scores, applied filters, and pagination info

## Files to Look At

- `packages/builtin-tool-memory/src/manifest.ts` — Tool manifest defining API schemas
- `packages/builtin-tool-memory/src/ExecutionRuntime/index.ts` — Runtime implementation
- `packages/builtin-tool-memory/src/types.ts` — Type definitions
- `packages/database/src/models/userMemory/model.ts` — Database model
- `packages/database/src/models/userMemory/query.ts` — New query layer (to be created)
- `packages/types/src/userMemory/tools.ts` — Tool parameter types
- `packages/builtin-tool-memory/src/systemRole.ts` — System role instructions
- `packages/builtin-tool-memory/promptfoo/tool-calls/memory-searchUserMemory.json` — Test fixture
- `locales/zh-CN/plugin.json` — Localization strings
- `src/locales/default/plugin.ts` — Default localization strings

## Key Changes Summary

1. Create new `UserMemoryQueryModel` class in `packages/database/src/models/userMemory/query.ts`
2. Update `SearchMemoryParams` type to use `queries` array instead of `query` string
3. Add `QueryTaxonomyOptionsParams` and `QueryTaxonomyOptionsResult` types
4. Update `MemoryExecutionRuntime.searchUserMemory()` to use new query model
5. Add `MemoryExecutionRuntime.queryTaxonomyOptions()` method
6. Update tool manifest with new schemas and the new `queryTaxonomyOptions` API
7. Update system role with new examples and usage guidelines
8. Update UI components to handle new result structure including identities

## Implementation Notes

- The new query layer uses hybrid search combining lexical (BM25) and semantic ranking
- Time intent selectors are resolved server-side into exact time ranges
- The taxonomy query merges values across all memory layers
- Backward compatibility: the `query` parameter is removed; callers must use `queries`
