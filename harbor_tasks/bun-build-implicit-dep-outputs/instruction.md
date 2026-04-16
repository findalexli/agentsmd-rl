# Build system: C/no-PCH C++ files do not recompile when dependency libraries change

## Symptom

When running the build twice after rebuilding a sub-build (e.g. WebKit) that updates forwarding headers, `.c` files and no-PCH `.cpp` files do not recompile even though their included headers changed. This produces stale object files and a relink that yields an inconsistent binary.

The build appears to lag one build behind: after the sub-build completes, the first main build uses stale object files; only on the second main build do affected sources recompile.

## Background

The ninja build system distinguishes between dependency types:
- **Implicit inputs** (`|`) — the dependent edge is invalidated when the input changes
- **Order-only inputs** (`||`) — enforces ordering but does not invalidate when the input changes

The compiler generates `.d` depfiles that record which headers were actually included. These depfiles let ninja track exact header dependencies on subsequent builds.

The build graph has a `depOutputs` array containing dependency library outputs like `libJavaScriptCore.a`. These library outputs come from sub-builds (like WebKit) that rewrite forwarding headers as undeclared side effects.

## Files to Modify

The build system is implemented in TypeScript files within the `scripts/build/` directory:

- `bun.ts` — contains `emitBun()` function that assembles the ninja build graph, including C compilation and no-PCH C++ compilation paths
- `compile.ts` — contains `CompileOpts` interface defining compilation options (`implicitInputs`, `orderOnlyInputs` fields)
- `CLAUDE.md` — documentation explaining ninja dependency types and build system concepts

## Root Cause

Local sub-builds (like WebKit) rewrite forwarding headers as undeclared side effects. The depfile records these headers, but ninja evaluates stats on the library before the sub-build completes. When order-only dependencies are used for the library outputs, ninja does not invalidate dependent compile edges even though the headers (tracked via depfile) have changed.

The library output itself (`libJavaScriptCore.a`) must serve as the invalidation signal. When the library changes, all compilation edges that may include its headers must be considered dirty. This applies to PCH compilation, C compilation, and no-PCH C++ compilation.

## Expected Correct Behavior

After modifying the build graph:
1. The build should not lag one build behind — C and no-PCH C++ sources should recompile on the first build after a sub-build updates forwarding headers
2. Codegen headers (from `codegen.cppAll`) should remain order-only — they are declared ninja outputs with restat, so depfile tracking is exact
3. Dependency library outputs (`depOutputs`) should trigger invalidation for PCH, C, and no-PCH C++ compilation
4. Documentation should correctly describe which dependency types use implicit vs order-only inputs and why

## Required Documentation Content

The verification checks for these literal strings in the modified files:

**CLAUDE.md Gotchas section** must contain:
- "PCH, cc, and no-PCH cxx" (or a pattern matching all three)
- "implicit dep on `depOutputs`"

**CLAUDE.md Ninja primer section** must show:
- An example with `deps/zstd/libzstd.a` as an implicit dependency (using `|`)
- Must NOT show the old pattern with `||` and `.ref` files

**CLAUDE.md depfile section** must explain:
- "implicit" dependencies for dep outputs
- "forwarding headers" or "undeclared side effect" of WebKit sub-builds

**bun.ts depOutputs comment** must:
- Mention "implicit-dep signal"
- NOT mention "PCH order-only-deps"

**compile.ts interface documentation** must:
- `implicitInputs`: mention "dep outputs" as "invalidation signal"
- `orderOnlyInputs`: redirect dep outputs to `implicitInputs` and clarify use for "codegen" headers

## Required Code Patterns

The verification checks for these patterns in `bun.ts`:

1. A variable containing `codegen.cppAll` for order-only use (to be used with `orderOnlyInputs`)
2. No variable combining both `depOutputs` and `codegen.cppAll` together
3. C compilation (`compileC`) passing `depOutputs` via `implicitInputs` and the codegen variable via `orderOnlyInputs`
4. No-PCH C++ compilation using the same pattern: `depOutputs` via `implicitInputs`, codegen variable via `orderOnlyInputs`

## Verification

After modifying the build graph, run the build command twice after rebuilding a sub-build that updates forwarding headers. All affected C and no-PCH C++ source files should recompile on the second run (the first main build after the sub-build), producing a consistent binary without requiring a third build.
