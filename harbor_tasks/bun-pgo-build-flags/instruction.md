# Add IR PGO build support

## Problem

The Bun build system currently does not support Profile-Guided Optimization (PGO). Developers cannot use `--pgo-generate` or `--pgo-use` flags when building Bun, which limits optimization opportunities for release builds.

## Expected Behavior

Add two new CLI flags to the build system:
- `--pgo-generate=<dir>` — produce an instrumented build that writes `.profraw` files at runtime
- `--pgo-use=<file.profdata>` — produce an optimized build using merged profile data

These flags should be implemented across the build system's TypeScript configuration layer, using the internal field names `pgoGenerate` and `pgoUse` throughout.

### 1. CLI Argument Parsing (`scripts/build.ts`)

The flags should be recognized by the CLI argument parser. Add `"pgoGenerate"` and `"pgoUse"` to the long options list alongside the existing options (around line 314).

### 2. Config Interface (`scripts/build/config.ts`)

**Config interface** — add two new fields with types `string | undefined`:
- `pgoGenerate: string | undefined`
- `pgoUse: string | undefined`

**PartialConfig interface** — add corresponding optional fields:
- `pgoGenerate?: string`
- `pgoUse?: string`

**resolveConfig function** — the function should:
- Resolve paths using `resolve(partial.pgoGenerate)` and `resolve(partial.pgoUse)` (or equivalent ternary like `partial.pgoGenerate ? resolve(...)`), assigning to local constants
- Validate mutual exclusivity: check the condition `pgoGenerate && pgoUse` (after resolving), and when true, throw a `BuildError` with the exact message: `--pgo-generate and --pgo-use are mutually exclusive`
- Include the resolved `pgoGenerate` and `pgoUse` in the returned Config object

**formatConfig function** — add feature labels to the features list:
- `if (cfg.pgoGenerate) features.push("pgo-gen")`
- `if (cfg.pgoUse) features.push("pgo-use")`

### 3. Compiler and Linker Flags (`scripts/build/flags.ts`)

Add PGO-related entries to both the `globalFlags` and `linkerFlags` arrays. Each entry is an object with `flag`, `when`, and `desc` fields (following the existing pattern).

**In `globalFlags`** — add a section with the header comment `─── PGO (compile-side) ───` containing:
- An entry for instrumentation with flag `-fprofile-generate=${c.pgoGenerate}`, gated on `c.unix && !!c.pgoGenerate`, with description `IR PGO: instrument for profile generation`
- An entry for optimization with flags `-fprofile-use=${c.pgoUse}` plus the warning suppressions `-Wno-profile-instr-out-of-date`, `-Wno-profile-instr-unprofiled`, `-Wno-backend-plugin`, gated on `c.unix && !!c.pgoUse`, with description `IR PGO: optimize with profile data`

**In `linkerFlags`** — add a section with the header comment `─── PGO (link-side) ───` containing:
- An entry for the profiling runtime with flag `-fprofile-generate=${c.pgoGenerate}`, gated on `c.unix && !!c.pgoGenerate`
- An entry for LTO+PGO at link time with flag `-fprofile-use=${c.pgoUse}`, gated on `c.unix && !!c.pgoUse`

This ensures `-fprofile-generate=` and `-fprofile-use=` each appear in both the compile and link flag arrays.

### 4. WebKit Dependency (`scripts/build/deps/webkit.ts`)

Forward PGO optimization flags to WebKit when building locally:
- Collect optimization flags (LTO and PGO) into an array variable named `optFlags`
- Join them into a string variable named `optFlagStr`
- Set the CMAKE args as object properties: `CMAKE_C_FLAGS: optFlagStr` and `CMAKE_CXX_FLAGS: optFlagStr` (instead of the previous empty strings)
- The `optFlags` array should check `cfg.pgoGenerate` and `cfg.pgoUse` and include `-fprofile-generate=` and `-fprofile-use=` flags accordingly
- When `cfg.pgoUse` is set, also include the warning suppression flags in `optFlags`

### Notes

- The flags should only apply on Unix platforms (check `c.unix`)
- The existing `lto` flag pattern in each file is a good reference for implementation style
- Follow the existing code formatting and comment conventions in each file
