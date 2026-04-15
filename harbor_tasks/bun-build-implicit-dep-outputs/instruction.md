# Build system: C/no-PCH C++ files do not recompile when dependency libraries change

## Symptom

When running the build twice after rebuilding a sub-build (e.g. WebKit) that updates forwarding headers, `.c` files and no-PCH `.cpp` files do not recompile even though their included headers changed. This produces stale object files and a relink that yields an inconsistent binary.

## Background

The ninja build system distinguishes between dependency types:
- **Implicit inputs** (`|`) — the dependent edge is invalidated when the input changes
- **Order-only inputs** (`||`) — enforces ordering but does not invalidate when the input changes

The compiler generates `.d` depfiles that record which headers were actually included. These depfiles let ninja track exact header dependencies on subsequent builds.

The build graph has a `depOutputs` array containing dependency library outputs like `libJavaScriptCore.a`. These library outputs come from sub-builds (like WebKit) that rewrite forwarding headers as undeclared side effects.

## Specific Values Required for Fix Verification

The following variable names, field names, and patterns appear in the build system code and will be verified by tests:

**Variable Names:**
- `depOutputs` — array of dependency library outputs (e.g., `libJavaScriptCore.a`)
- `codegen.cppAll` — array of codegen-generated C++ sources
- `codegenOrderOnly` — variable name that must appear in the fixed build graph
- `depOrderOnly` — variable name from the original build graph that must be removed

**Interface Fields:**
- `implicitInputs` — field for implicit dependencies that invalidate on change
- `orderOnlyInputs` — field for order-only dependencies

**Required Assignment Patterns:**
- `const codegenOrderOnly = codegen.cppAll` — the variable `codegenOrderOnly` must be defined exactly as `codegen.cppAll`
- `implicitInputs: depOutputs` — for C compilation, the `depOutputs` must be passed via `implicitInputs`
- `orderOnlyInputs: codegenOrderOnly` — for C compilation, codegen headers must be passed via `orderOnlyInputs`
- `implicitInputs = depOutputs` — for no-PCH C++ compilation, `depOutputs` must be assigned to `implicitInputs`
- `orderOnlyInputs = codegenOrderOnly` — for no-PCH C++ compilation, `codegenOrderOnly` must be assigned to `orderOnlyInputs`

**Required Documentation in CLAUDE.md:**
- Gotchas section must mention "PCH, cc, and no-PCH cxx" together
- Gotchas section must contain the phrase "implicit dep on `depOutputs`"
- Ninja primer example must show a dep output (like `deps/zstd/libzstd.a`) as implicit dependency (using `|`), not order-only
- depfile section must explain that WebKit sub-builds rewrite forwarding headers as undeclared side effects
- depfile section must distinguish codegen headers (order-only, declared ninja outputs with restat) from dep outputs (`lib*.a`)
- depOutputs variable comment must describe "implicit-dep signal" (not "PCH order-only-deps")
- `implicitInputs` documentation must mention "dep outputs" and "invalidation signal"
- `orderOnlyInputs` documentation must redirect dep outputs to `implicitInputs`

## Expected Behavior After Fix

After modifying the build system:
1. The variable `depOrderOnly` (which combined `depOutputs` and `codegen.cppAll`) must be removed
2. A new variable `codegenOrderOnly` defined as `codegen.cppAll` must exist
3. C compilation must pass `depOutputs` via `implicitInputs` and `codegenOrderOnly` via `orderOnlyInputs`
4. No-PCH C++ compilation must use `implicitInputs` with `depOutputs` and `orderOnlyInputs` with `codegenOrderOnly`
5. Documentation must correctly describe the dependency model for codegen headers vs dep outputs

## Root Cause

The ninja build graph uses order-only dependencies for dep library outputs in C compilation and no-PCH C++ compilation. Order-only dependencies only enforce ordering — they do not invalidate the dependent compile edge when the library itself changes. Since the dep library's forwarding headers are rewritten as undeclared side effects, the compiler's depfile records those headers, but ninja evaluates stats on the lib before the sub-build completes, so order-only does not trigger invalidation.

## Files Involved

The relevant files are within the build system scripts directory:
- TypeScript source files containing the ninja build graph assembly
- TypeScript files containing compilation interfaces
- Markdown documentation files covering ninja dependency types

## Verification

After modifying the build graph, run the build command twice after rebuilding a sub-build that updates forwarding headers. All affected C and no-PCH C++ source files should recompile on the second run, producing a consistent binary.
