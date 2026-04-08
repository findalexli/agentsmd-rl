# Build system: C/no-PCH C++ files use wrong ninja dependency type for dep outputs

## Problem

Running `build:release:local` twice after a WebKit rebuild causes a spurious relink. C files (and C++ files when PCH is disabled) only have order-only dependencies on dep library outputs. This means they lag one build behind when dep sub-builds (like WebKit) rewrite forwarding headers as undeclared side effects — the compiler's depfile records those headers, but ninja stats them before the sub-build runs, so order-only doesn't invalidate.

The symptom: after rebuilding a dep that updates forwarding headers, `.c` and no-PCH `.cpp` files don't recompile even though their included headers changed, leading to stale object files and a relink that produces an inconsistent binary.

## Expected Behavior

C compilation (`cc()`) and no-PCH C++ compilation (`cxx()` without PCH) should use **implicit** dependencies on dep outputs (e.g. `libJavaScriptCore.a`), not order-only. The implicit dep makes the lib itself the invalidation signal — when the dep is rebuilt, all compile edges that depend on it are invalidated. Codegen headers should remain as order-only deps since they're declared ninja outputs with `restat`, so depfile tracking is exact.

## Files to Look At

- `scripts/build/bun.ts` — the `emitBun` function assembles the ninja build graph. The `compileC` lambda and the no-PCH `cxx` path both need to pass dep outputs as `implicitInputs` instead of `orderOnlyInputs`. The variable that was `depOrderOnly` (combining dep outputs + codegen) should be split so only codegen headers stay order-only.
- `scripts/build/compile.ts` — the `CompileOpts` interface defines `implicitInputs` and `orderOnlyInputs`. Their doc comments should be updated to explain when to use each for dep outputs vs codegen headers.
- `scripts/build/CLAUDE.md` — the build system documentation. The ninja primer, edge dependency descriptions, depfile explanation, and Gotchas section all reference the dependency model and should be updated to reflect that dep outputs are implicit deps (not order-only) for PCH, cc, and no-PCH cxx. The documentation should explain why: local sub-builds rewrite forwarding headers as undeclared side effects, so the lib is the invalidation signal.
