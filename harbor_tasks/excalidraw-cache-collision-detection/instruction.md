# Add Caching to Collision Detection

## Problem

The `hitElementItself` function in `packages/element/src/collision.ts` is called frequently during mouse interactions to determine if a point hits an element. Without caching, repeated hit tests on the same point and element are expensive.

## Goal

Add a caching mechanism so that when the same point and element are tested again with conditions that allow reuse, the cached result is returned instead of recomputing.

## What the Tests Check

The tests verify specific string patterns must be present in the code:

- Cache variables exist: `cachedPoint`, `cachedElement`, `cachedThreshold`, `cachedHit`
- The cache uses: `WeakRef`, `pointsEqual`
- Threshold comparison uses `<=` (not `>=`)
- Threshold is stored after computing result
- Point equality check: `pointsEqual(point, cachedPoint)`
- Element dereferencing: `cachedElement?.deref()`
- Version checks: `derefElement.version === element.version`, `derefElement.versionNonce === element.versionNonce`
- Result pattern: the hit result is stored and returned; look for `result = hitElement || hitFrameName` (or const variant)
- Cache storage: `cachedHit = result` appears in the code
- Cache return: `return cachedHit` appears in the code

## Files to Modify

- `packages/element/src/collision.ts`

## Verification

After implementing:

```bash
cd /workspace/excalidraw
yarn test:typecheck
yarn vitest run packages/element/tests/collision.test.tsx
```