# Refactor build commands for clarity and consistency

## Problem

The `waspc/run` script's build command naming is confusing. Currently:

- `./run build` only builds the Haskell project, which is misleading since you'd expect `build` to build everything.
- `./run build:all` builds Haskell + TypeScript packages — this is what most developers actually want.
- `./run build:all:static` is a separate command just to add `--enable-executable-static` to the build.

This naming trips up new contributors who run `./run build` expecting a full build but only get the Haskell part.

## Expected Behavior

The command names should be intuitive:

- `build` should build everything (Haskell + TS packages) — the common case.
- A new `build:hs` command should exist for Haskell-only builds.
- Static builds should be controlled via the `BUILD_STATIC` environment variable, not a separate command.
- The `build:all` and `build:all:static` commands should be removed.
- The existing `build:packages` command must be preserved unchanged.

### Bash run script (`waspc/run`)

The script already defines variables like `BUILD_HS_CMD`, `BUILD_ALL_CMD`, and `BUILD_ALL_STATIC_CMD`. After the refactor:

- The `BUILD_ALL_CMD` variable must remain defined and represent the full build (packages + Haskell).
- The `BUILD_HS_CMD` variable must remain defined for Haskell-only builds and should incorporate the `BUILD_STATIC` env var to conditionally pass `--enable-executable-static`.
- The `BUILD_ALL_STATIC_CMD` variable must be removed entirely.
- In the `case $COMMAND in` dispatch block:
  - `build)` must invoke `$BUILD_ALL_CMD` via `echo_and_eval`
  - `build:hs)` must exist and invoke `$BUILD_HS_CMD` via `echo_and_eval`
  - `build:all)` and `build:all:static)` must be removed from the case statement

### PowerShell script (`waspc/run.ps1`)

The PowerShell `switch ($Command)` block must be updated to match:

- The `"build"` case must invoke `BUILD_ALL_CMD` (the full build)
- A `"build:hs"` case must exist and invoke `BUILD_HS_CMD`

### CI workflow (`.github/workflows/ci-waspc-build.yaml`)

- The build step must use `./run build` (not `./run build:all`)
- Static builds should be driven by the `BUILD_STATIC` environment variable set from the CI matrix

## Files to Look At

- `waspc/run` — main build script with variable definitions and case dispatch
- `waspc/run.ps1` — PowerShell equivalent of the run script
- `.github/workflows/ci-waspc-build.yaml` — CI build workflow
