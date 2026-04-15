# Build system: C/no-PCH C++ files use wrong ninja dependency type for dep outputs

## Symptom

When running `build:release:local` twice after rebuilding a sub-build (e.g. WebKit) that updates forwarding headers, `.c` files and no-PCH `.cpp` files do not recompile even though their included headers changed. This produces stale object files and a relink that yields an inconsistent binary.

## Root Cause

The ninja build graph currently uses **order-only** dependencies for dep library outputs (like `libJavaScriptCore.a`) in C compilation and no-PCH C++ compilation. Order-only dependencies only enforce ordering — they do not invalidate the dependent compile edge when the library itself changes. Since the dep library's forwarding headers are rewritten as undeclared side effects, the compiler's depfile records those headers, but ninja evaluates stats on the lib before the sub-build completes, so order-only does not trigger invalidation.

## Expected Behavior

C compilation and no-PCH C++ compilation should use **implicit** dependencies on dep outputs. The implicit dep makes the library itself the invalidation signal — when the dep is rebuilt, all compile edges that depend on it are invalidated. Codegen headers (generated headers that are declared ninja outputs with `restat`) should remain order-only since their depfile tracking is exact.

## Files to Inspect

- `scripts/build/bun.ts` — the `emitBun` function assembles the ninja build graph
- `scripts/build/compile.ts` — the `CompileOpts` interface documents `implicitInputs` and `orderOnlyInputs`
- `scripts/build/CLAUDE.md` — build system documentation covering ninja dependency types

## Verification

After modifying the build graph, run `build:release:local` twice after rebuilding a sub-build that updates forwarding headers. All affected C and no-PCH C++ source files should recompile on the second run, producing a consistent binary.

## Key Concepts

- **Implicit dependency (`|`)**: The dependent edge is invalidated when the output changes. Use for dep library outputs.
- **Order-only dependency (`||`)**: Enforces ordering but does not invalidate the dependent edge. Use for codegen headers (declared ninja outputs with `restat`).
- **depfile**: Records header dependencies; ninja stats the file timestamps before sub-builds run, so order-only does not capture the invalidation signal for dep outputs.

The ninja primer in CLAUDE.md explains these dependency types in detail. The `**depfile**` section documents why order-only fails for dep outputs when sub-builds rewrite forwarding headers as undeclared side effects. The Gotchas section covers when each dependency type is appropriate.
