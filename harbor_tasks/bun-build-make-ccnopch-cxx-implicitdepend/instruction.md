# build: make cc/no-PCH cxx implicit-depend on dep outputs

## Problem

After a local WebKit rebuild, the second `build:release:local` run triggers a spurious full relink. C files and C++ files without precompiled headers (no-PCH `cxx`) have their compile edges lag one build behind: they don't re-run when a dep library is rebuilt, even though the dep's sub-build may have rewritten forwarding headers as an undeclared side effect. The result is stale objects and a full relink on the next build.

The root cause is that `cc()` and no-PCH `cxx()` calls in `scripts/build/bun.ts` use `orderOnlyInputs` for dependency library outputs (`depOutputs`), which only ensures the libraries exist before compiling but doesn't consider the library's timestamp as a reason to recompile. Since depfile tracking for forwarding headers happens after the compilation, the stale objects aren't detected until the next build.

## Expected Behavior

When a dep library is rebuilt (and its forwarding headers potentially changed), all affected compile edges (`cc` and no-PCH `cxx`) should re-run immediately instead of lagging one build behind. The `lib*.a` files from dependency builds should provide an effective invalidation signal for the compile edges that depend on them.

Codegen headers should remain as order-only dependencies since they are declared Ninja outputs with `restat` and depfile tracking is exact for them.

## Files to Look At

- `scripts/build/bun.ts` — examine the `compileC` function and the no-PCH `cxx` code path (the `else` branch when PCH is disabled); look at how dependencies on `depOutputs` are structured
- `scripts/build/compile.ts` — `CompileOpts` interface with `implicitInputs` and `orderOnlyInputs` options
- `scripts/build/CLAUDE.md` — Ninja primer and Gotchas sections document the dependency strategy

## What You Need to Do

1. **Fix C compilation invalidation**: C files must recompile when dependency libraries are rebuilt. Find where `.c` files are compiled via `cc()` in the `compileC` function. Currently these use `orderOnlyInputs` for `depOutputs`, which prevents rebuild triggering. The compile edges for `.c` files should treat dependency library outputs as invalidation triggers.

2. **Fix no-PCH C++ compilation invalidation**: When PCH is disabled (e.g., on Windows), C++ files must also recompile when dependency libraries are rebuilt. Find the no-PCH code path (the `else` branch when `pch_file` is not set). This path currently uses `orderOnlyInputs` for `depOutputs` and needs the same fix as C files.

3. **Separate dep outputs from codegen**: The build graph must distinguish between:
   - Dependency library outputs (`lib*.a` files) that serve as invalidation signals when rebuilt
   - Codegen headers (declared Ninja outputs with `restat`) which should remain order-only

   The current code mixes `depOutputs` and `codegen.cppAll` together. Separate them into distinct variables: one for library outputs (to be used as implicit deps) and one for codegen headers (to remain as order-only).

4. **Update CLAUDE.md documentation**: The Gotchas section currently has outdated/incorrect guidance about "cxx needs order-only dep on depOutputs". This is wrong — both C files and no-PCH C++ files need dependency library outputs to trigger invalidation, just like PCH does. Update the documentation to explain that:
   - PCH compilation, C compilation, and no-PCH C++ compilation all need dependency library outputs (`depOutputs`) as implicit dependencies
   - Codegen headers remain order-only because they are declared outputs with proper restat tracking
   - Local WebKit sub-builds rewrite forwarding headers as undeclared side effects, so the library files themselves serve as the invalidation signal

## Implementation Context

Ninja's dependency model offers two relevant dependency types:
- **Implicit dependencies** (`| deps`) — the target is checked for modification and will trigger rebuilds if changed
- **Order-only dependencies** (`|| stamp`) — only ensures the dependency exists before the target runs, but doesn't trigger rebuilds when modified

The current implementation incorrectly uses order-only dependencies for dependency library outputs, which prevents the rebuild triggering behavior needed.

The `CompileOpts` interface in `compile.ts` supports both `implicitInputs` and `orderOnlyInputs`. The fix involves changing which option is used for `depOutputs` while keeping `codegen.cppAll` as order-only.
