# Make search param patterns consistent with URLSearchParams

## Problem

The `RoutePattern` class in `packages/route-pattern/` treats `?q` and `?q=` as different constraints. `?q` means "key must be present" while `?q=` means "key must be present with a non-empty value." This is inconsistent with how `URLSearchParams` works — to the web platform, `?q` and `?q=` are the same thing (both produce key `q` with value `""`).

This inconsistency causes unintuitive matching behavior. For example, `new RoutePattern('?q=').match(url)` returns `null` when the URL has `?q=` in it — even though the pattern search and URL search look identical.

Additionally, `parseSearch` uses manual `decodeURIComponent` for decoding, which doesn't decode `+` as a space the way `URLSearchParams` does. This means `?q=a+b` stores the literal string `a+b` rather than `a b`.

## Expected Behavior

- `?q` and `?q=` should be treated as the **same** constraint: key must be present; value may be anything (including empty).
- Parsing should use `URLSearchParams` (or equivalent WHATWG `application/x-www-form-urlencoded` decoding) so that `+` is decoded as a space.
- Serialization should produce output consistent with `URLSearchParams`, e.g. key-only `?q` should serialize to `q=` (not bare `q`).
- The `missing-search-params` error in `href()` is no longer needed once the "key with any value" constraint is removed.

## Files to Look At

- `packages/route-pattern/src/lib/route-pattern/parse.ts` — search param parsing logic
- `packages/route-pattern/src/lib/route-pattern/match.ts` — search param matching
- `packages/route-pattern/src/lib/route-pattern/serialize.ts` — search param serialization
- `packages/route-pattern/src/lib/route-pattern/href.ts` — href generation with search params
- `packages/route-pattern/src/lib/route-pattern/join.ts` — pattern joining for search
- `packages/route-pattern/src/lib/specificity.ts` — specificity comparison for search constraints
- `packages/route-pattern/src/lib/route-pattern.ts` — AST type definitions

After fixing the code, update the package's README to reflect the new search param behavior. The documentation currently describes `?q` and `?q=` as different constraints — it should be updated to accurately document the new semantics.
