# Refactor route-pattern helpers into PartPattern methods

The `packages/route-pattern/src/lib/route-pattern/` directory contains several helper modules that are currently organized by pattern part (e.g., `source.ts` for source serialization) and imported via namespace imports (`import * as Source from './source.ts'`).

## Problems

1. **`source.ts` contains logic that belongs on the `PartPattern` class itself.** The `Source.part()` function serializes a PartPattern back to its source string — this is fundamentally a `PartPattern` operation, not a standalone utility. Similarly, `Source.search()` serializes search constraints, which should live in its own focused module.

2. **Namespace imports make the code harder to navigate.** Functions like `Parse.protocol()`, `Source.part()`, `Href.part()`, `Join.pathname()`, and `Search.test()` aren't autocomplete-friendly and are inconsistent with how the rest of the Remix codebase is organized. They should be replaced with named imports.

3. **The `toRegExp` standalone function in `part-pattern.ts` accesses PartPattern internals directly.** It should be a private method on the class.

## What to do

Refactor the helper modules in `packages/route-pattern/src/lib/route-pattern/`:

- Move the source serialization logic from `source.ts` into `PartPattern` as a `source` getter (the `search` serialization should move to a new `serialize.ts` module)
- Move the href generation logic from `href.ts`'s `part()` function into `PartPattern` as an `href()` method
- Make `toRegExp` a private `#toRegExp()` method on `PartPattern`
- Replace namespace imports with named imports across all files that import from these helpers
- Rename `search.ts` to `match.ts` (since it now only contains URL matching logic) and rename its `test()` export to `matchSearch()`
- Rename the parse functions from `Parse.protocol()` → `parseProtocol()`, etc.
- Rename the join functions from `Join.pathname()` → `joinPathname()`, etc.
- Delete `source.ts` entirely
- Update all callers in `route-pattern.ts`, `route-pattern.test.ts`, `part-pattern.test.ts`, and `trie-matcher.ts`

After refactoring the code, create an `AGENTS.md` file in `packages/route-pattern/src/lib/route-pattern/` that documents how the helper files are organized. The documentation should explain that `part-pattern.ts` contains logic for any PartPattern, while other files are organized by feature (href, join, match, parse, serialize, split). Reference the parent `route-pattern.ts` module.

## Files to modify

- `packages/route-pattern/src/lib/route-pattern.ts`
- `packages/route-pattern/src/lib/route-pattern/part-pattern.ts`
- `packages/route-pattern/src/lib/route-pattern/href.ts`
- `packages/route-pattern/src/lib/route-pattern/parse.ts`
- `packages/route-pattern/src/lib/route-pattern/join.ts`
- `packages/route-pattern/src/lib/route-pattern/source.ts` (delete)
- `packages/route-pattern/src/lib/route-pattern/search.ts` (rename to `match.ts`)
- `packages/route-pattern/src/lib/route-pattern/serialize.ts` (new)
- `packages/route-pattern/src/lib/route-pattern/AGENTS.md` (new)
- `packages/route-pattern/src/index.ts`
- `packages/route-pattern/src/lib/route-pattern.test.ts`
- `packages/route-pattern/src/lib/route-pattern/part-pattern.test.ts`
- `packages/route-pattern/src/lib/trie-matcher.ts`

All existing tests must continue to pass.
