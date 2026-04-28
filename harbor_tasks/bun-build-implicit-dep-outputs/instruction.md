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

## Documentation Requirements

The modified `CLAUDE.md` must correctly explain the ninja dependency types used for different categories of inputs. Specifically:

**Gotchas section** — must explain that dependency library outputs (like `libJavaScriptCore.a`) use implicit dependencies, not order-only, because local sub-builds rewrite forwarding headers as undeclared side effects and only the library itself serves as a reliable invalidation signal.

**Ninja primer section** — must include an example showing that library outputs use implicit dependencies (`|`), not order-only (`||`).

**depfile section** — must explain the distinction between codegen headers (order-only, tracked via depfile) and dep outputs (implicit, used as invalidation signal), including the WebKit forwarding header side effect explanation.

**`bun.ts` depOutputs comment** — must describe the role of `depOutputs` as an invalidation signal for compilation edges, not just for PCH.

**`compile.ts` CompileOpts documentation** — must explain the purpose of `implicitInputs` (for dep outputs as invalidation signal) and `orderOnlyInputs` (for codegen headers that are declared ninja outputs with restat).

## Code Structure Requirements

The modified `bun.ts` must separate dependency tracking for order-only inputs from invalidation signals:

1. There must be a variable used with `orderOnlyInputs` that contains only `codegen.cppAll` (not `depOutputs`)
2. The old variable that combined `depOutputs` with `codegen` must be removed
3. C compilation (`compileC`) must pass `depOutputs` via `implicitInputs` and the order-only codegen variable via `orderOnlyInputs`
4. No-PCH C++ compilation must use the same pattern: `depOutputs` via `implicitInputs`, codegen variable via `orderOnlyInputs`

## Verification

After modifying the build graph, run the build command twice after rebuilding a sub-build that updates forwarding headers. All affected C and no-PCH C++ source files should recompile on the second run (the first main build after the sub-build), producing a consistent binary without requiring a third build.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `oxlint (TypeScript linter)` — for TypeScript build scripts
- `markdownlint (Markdown linter)` — for CLAUDE.md documentation
- `editorconfig-checker` — for file encoding, trailing whitespace, and final newline compliance
