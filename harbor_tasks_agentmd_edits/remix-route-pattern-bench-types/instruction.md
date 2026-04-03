# Add type benchmarks for route-pattern

## Problem

The `packages/route-pattern/bench/` directory currently only has runtime benchmarks (using Vitest) that measure execution speed. There are no benchmarks tracking TypeScript type-level performance — how many type instantiations operations like `href()`, `join()`, `match().params`, and `new RoutePattern()` require.

Additionally, the runtime benchmark files sit directly in the `bench/` root alongside the README and package.json, which will get cluttered as more benchmarks are added.

## Expected Behavior

1. **Reorganize runtime benchmarks** into a `bench/src/` subdirectory so the bench directory stays organized.
2. **Add type benchmarks** in a `bench/types/` subdirectory that use a type benchmarking tool to track TypeScript type instantiation counts for the key route-pattern APIs: `href`, `join`, `params`, and the `RoutePattern` constructor.
3. **Move the `@ark/attest` dependency** from `packages/route-pattern/` to `packages/route-pattern/bench/` since it's only used for benchmarks, not the library itself.
4. **Add a `bench:types` script** to `bench/package.json` for running the type benchmarks.
5. **Update `bench/README.md`** to document both the runtime and type benchmarks, including what directory each lives in and what tool each uses. The existing runtime benchmarks documentation should be restructured to distinguish them from the new type benchmarks.

## Files to Look At

- `packages/route-pattern/bench/` — benchmark directory to reorganize and extend
- `packages/route-pattern/bench/README.md` — needs updating to document the new benchmark structure
- `packages/route-pattern/bench/package.json` — needs new script and dependency
- `packages/route-pattern/package.json` — `@ark/attest` should be moved out of here
