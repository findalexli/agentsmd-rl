# Add type benchmarks to route-pattern bench package

## Problem

The `packages/route-pattern/bench/` directory currently only has runtime benchmarks (using Vitest benchmarking). There are no benchmarks for TypeScript type-level performance — specifically how many type instantiations are needed for core operations like `RoutePattern` construction, `href()`, `join()`, `match()`, and their corresponding type utilities (`HrefArgs`, `Join`, `Params`).

Additionally, the existing benchmark files in `packages/route-pattern/bench/` are flat — they're not organized by benchmark category.

## Expected Behavior

1. Add type benchmarks that measure type instantiation counts for `RoutePattern` operations, using [ArkType Attest](https://github.com/arktypeio/arktype/blob/main/ark/attest/README.md). Create benchmark files for:
   - `new RoutePattern()` construction
   - `pattern.href()` calls and the `HrefArgs` type
   - `pattern.join()` calls and the `Join` type
   - `pattern.match()` params extraction and the `Params` type

2. Move the existing runtime benchmark files into a `src/` subdirectory to separate them from the new type benchmarks.

3. Update `packages/route-pattern/bench/package.json`:
   - Add a `bench:types` script for running type benchmarks
   - Add `@ark/attest` as a devDependency (this should live in the bench package, not the parent route-pattern package)

4. Update `packages/route-pattern/bench/README.md` to document:
   - The distinction between runtime benchmarks and type benchmarks
   - How to run type benchmarks
   - The new `src/` and `types/` directory organization

## Files to Look At

- `packages/route-pattern/bench/` — benchmark directory to restructure
- `packages/route-pattern/bench/README.md` — documentation to update
- `packages/route-pattern/bench/package.json` — scripts and dependencies
- `packages/route-pattern/package.json` — parent package (move @ark/attest dep out)
- `packages/route-pattern/src/lib/route-pattern/AGENTS.md` — codebase organization guide
