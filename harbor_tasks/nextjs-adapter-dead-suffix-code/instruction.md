# Dead code in adapter build-complete suffix handling

## Context

In `packages/next/src/build/adapter/build-complete.ts`, the `handleBuildComplete` function constructs dynamic route entries for RSC (React Server Components) suffix rewrites.

## Problem

There is a conditional variable that controls which regex pattern to use for RSC suffix matching. However, both branches of the conditional produce the **exact same regex string**. This means:

1. A boolean flag is destructured from the route object and stored in a local variable, but it has no actual effect on the output.
2. A `const` is assigned based on this flag, but it's meaningless since both paths are identical.
3. A ternary expression in the `sourceRegex.replace()` call selects between two identical regex patterns.

Additionally, the type definition for `ManifestRoute` in `packages/next/src/build/index.ts` declares an optional property that backs this dead flag — it is never meaningfully consumed.

## Expected outcome

Remove the dead code path:
- Eliminate the unused flag destructuring and the derived conditional variable
- Replace the ternary with the single regex pattern directly
- Remove the unused optional property from the `ManifestRoute` type
- Remove associated comments that describe the now-removed logic

The resulting behavior must be identical — no functional changes, just dead code cleanup.

## Files of interest

- `packages/next/src/build/adapter/build-complete.ts` — the conditional logic around suffix regex
- `packages/next/src/build/index.ts` — the `ManifestRoute` type definition
