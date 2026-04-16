# Add IR PGO build support to Bun

## Background

The Bun build system currently lacks Profile-Guided Optimization (PGO) support. Developers cannot leverage PGO workflows for release builds.

## Required Behavior

### CLI Flag Recognition

The build system's argument parser must accept two new flags:
- `--pgo-generate=<directory>` — enables an instrumented build that writes `.profraw` files at runtime
- `--pgo-use=<file.profdata>` — enables an optimized build using merged profile data

When a user passes an unknown flag like `--pgo-generate`, the build system should not silently ignore it — it should be recognized and processed.

### Mutual Exclusivity

The two flags are mutually exclusive. When a user attempts to use both `--pgo-generate` and `--pgo-use` in the same build, the build system must fail with a clear error. The error message must be:

```
--pgo-generate and --pgo-use are mutually exclusive
```

### Feature Label Reporting

When PGO is active, the build system should report it in its feature output. The feature label for an instrumented (generate) build must be: `pgo-gen`. The feature label for an optimized (use) build must be: `pgo-use`.

### Compiler and Linker Flags

When `--pgo-generate` is active on a Unix platform, the compiler must receive `-fprofile-generate=<dir>` where `<dir>` is the provided directory path.

When `--pgo-use` is active on a Unix platform, the compiler must receive `-fprofile-use=<file>` along with warning suppression flags `-Wno-profile-instr-out-of-date`, `-Wno-profile-instr-unprofiled`, and `-Wno-backend-plugin`.

These flags must be passed to both the compiler (compile-time) via `globalFlags` in `scripts/build/flags.ts` and to the linker (link-time) via `linkerFlags` in `scripts/build/flags.ts`.

### WebKit Build Integration

When building WebKit locally, the PGO flags must be forwarded to WebKit's CMake configuration via `CMAKE_C_FLAGS` and `CMAKE_CXX_FLAGS`. This is done by calling `webkit.build()` from `scripts/build/deps/webkit.ts` with the resolved config.

When `--pgo-use` is set, the warning suppression flags must also be included.

### Platform Constraint

All PGO flags apply only on Unix platforms (Linux and macOS). On Windows, the flags have no effect.

### Config Schema

The resolved config object (returned by `resolveConfig()` from `scripts/build/config.ts`) must preserve the following properties when set:
- `pgoGenerate` — the directory path provided to `--pgo-generate`
- `pgoUse` — the file path provided to `--pgo-use`

## Verification

A correct implementation can be verified by:
1. Running the build with `--pgo-generate=/tmp/pgo-data` and confirming the build starts with the feature label `pgo-gen` reported
2. Running the build with `--pgo-use=./merged.profdata` and confirming the build starts with the feature label `pgo-use` reported
3. Running the build with both flags and confirming the build fails with the exact error message `--pgo-generate and --pgo-use are mutually exclusive`
4. Inspecting the compiler and linker flags in the build output to confirm `-fprofile-generate=` and `-fprofile-use=` appear