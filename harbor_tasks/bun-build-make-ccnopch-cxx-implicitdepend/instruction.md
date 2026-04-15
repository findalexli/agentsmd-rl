# build: make cc/no-PCH cxx implicit-depend on dep outputs

## Problem

After a local WebKit rebuild, the second `build:release:local` run triggers a spurious full relink. C files (compiled via the `cc` rule) and C++ files without precompiled headers (no-PCH `cxx`) have their compile edges lag one build behind: they don't re-run when a dep library is rebuilt, even though the dep's sub-build may have rewritten forwarding headers as an undeclared side effect. The result is stale objects and a full relink on the next build.

## Expected Behavior

When a dep library is rebuilt (and its forwarding headers potentially changed), all affected compile edges (`cc` and no-PCH `cxx`) should re-run immediately instead of lagging one build behind. The `lib*.a` files from dependency builds should provide an effective invalidation signal for the compile edges that depend on them.

Codegen headers should remain as they are since they are declared Ninja outputs with `restat` and depfile tracking is exact for them.

## Files to Look At

- `scripts/build/bun.ts` — look at how `emitBun()` assembles the build graph; look at how `cc()` and `cxx()` calls structure their dependencies
- `scripts/build/compile.ts` — `CompileOpts` interface documents `implicitInputs` and `orderOnlyInputs` options
- `scripts/build/CLAUDE.md` — Ninja primer and Gotchas sections document the dependency strategy

## Documentation Update

The `scripts/build/CLAUDE.md` documentation must also be updated to reflect the corrected dependency strategy.

## Specific Requirements

The fix must satisfy the following behavioral requirements, which will be verified:

1. The `cc()` calls within the `compileC` function must pass `depOutputs` as `implicitInputs` (not `orderOnlyInputs`) to ensure C compilation triggers when deps rebuild.

2. The no-PCH `cxx` code path (triggered when PCH is disabled, e.g., on Windows) must also pass `depOutputs` as `implicitInputs` to ensure C++ files without PCH properly invalidate when deps rebuild.

3. The build graph must separate `depOutputs` (library outputs that provide invalidation signals) from `codegen.cppAll` (codegen headers). These should not be combined in a single variable used for both implicit and order-only inputs. Codegen headers should remain order-only, while dep outputs should become implicit deps.

4. The `scripts/build/CLAUDE.md` file must be updated:
   - Remove any documentation suggesting that `cxx` needs order-only dependencies on `depOutputs`
   - Add documentation explaining that `cc`, PCH, and no-PCH `cxx` all need implicit dependencies on `depOutputs` (look for text matching patterns like "cc needs implicit dep" or "PCH.*cc.*cxx.*implicit")
