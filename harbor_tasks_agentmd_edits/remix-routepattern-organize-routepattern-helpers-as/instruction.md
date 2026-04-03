# Reorganize route-pattern helpers as PartPattern methods or by feature

## Problem

The `packages/route-pattern/src/lib/route-pattern/` directory has helpers organized in a way that's inconsistent and hard to navigate. Some functions that logically belong to `PartPattern` (like generating a source string or building an href from params) live in separate utility modules (`source.ts`, `href.ts`) as standalone functions that take a `PartPattern` as their first argument. Meanwhile, the search-related code is split across modules by pattern part rather than by feature.

Additionally, the main `route-pattern.ts` file uses namespace imports (`import * as Source from ...`, `import * as Href from ...`, etc.) which aren't autocomplete-friendly and are inconsistent with how the rest of the codebase uses imports.

## Expected Behavior

1. **Functions that operate on any `PartPattern`** (hostname and pathname alike) should be methods on the `PartPattern` class itself — specifically:
   - A `source` getter that reconstructs the pattern string from tokens
   - An `href()` method that generates a URL segment from params

2. **Remaining standalone helpers** should be organized by feature (href generation, joining, matching, parsing, serializing, splitting) rather than by pattern part. For example:
   - Search constraint serialization should live in its own `serialize.ts` module
   - The search matching logic (currently in `search.ts`) should be renamed to `match.ts` with a descriptive function name

3. **Namespace imports** in `route-pattern.ts` should be replaced with named imports for consistency and better IDE autocomplete.

4. After making these structural changes, **add an `AGENTS.md`** in the route-pattern helpers directory to document the new organizational conventions so future contributors know where to put new code.

## Files to Look At

- `packages/route-pattern/src/lib/route-pattern/part-pattern.ts` — the `PartPattern` class; add methods here
- `packages/route-pattern/src/lib/route-pattern/source.ts` — standalone `part()` and `search()` functions that should be moved
- `packages/route-pattern/src/lib/route-pattern/href.ts` — the `part()` function here should become a PartPattern method
- `packages/route-pattern/src/lib/route-pattern/search.ts` — search matching logic, should be renamed
- `packages/route-pattern/src/lib/route-pattern.ts` — main module with namespace imports to replace
- `packages/route-pattern/src/lib/route-pattern.test.ts` — tests that reference the old imports
- `packages/route-pattern/src/index.ts` — public API exports
