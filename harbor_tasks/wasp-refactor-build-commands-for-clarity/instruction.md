# Refactor build commands for clarity and consistency

## Problem

The `waspc/run` script's build command naming is confusing. Currently:

- `./run build` only builds the Haskell project, which is misleading since you'd expect `build` to build everything.
- `./run build:all` builds Haskell + TypeScript packages — this is what most developers actually want.
- `./run build:all:static` is a separate command just to add `--enable-executable-static` to the build.

This naming trips up new contributors who run `./run build` expecting a full build but only get the Haskell part.

## Expected Behavior

Rename and reorganize the build commands so that:

- `build` becomes the command that builds everything (Haskell + TS packages) — the common case.
- A new `build:hs` command provides Haskell-only builds for developers who don't need to rebuild TS packages.
- Static builds (which pass `--enable-executable-static` to cabal) should be controlled via the `BUILD_STATIC` environment variable (e.g., `BUILD_STATIC=1 ./run build`) instead of having a separate command.
- The `build:all` and `build:all:static` commands should be removed entirely.
- The existing `build:packages` command must be preserved unchanged.

These changes need to be applied consistently across all three files that define or invoke build commands:

- `waspc/run` — the main bash build script
- `waspc/run.ps1` — the PowerShell equivalent, which has a `switch` block mirroring the bash case dispatch
- `.github/workflows/ci-waspc-build.yaml` — the CI workflow, which currently invokes `./run build:all` and should use `./run build` instead
