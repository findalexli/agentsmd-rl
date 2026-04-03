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
- A more specific command should exist for Haskell-only builds.
- Static builds should not need a separate command — an environment variable is cleaner.

The rename needs to be applied consistently across:
- The bash `run` script (both command dispatch and help text)
- The PowerShell `run.ps1` script
- The CI workflow (`.github/workflows/ci-waspc-build.yaml`)

After making the code changes, update `waspc/README.md` to reflect the new command names. The README currently references the old commands in several places (the Build section, the "Run the wasp CLI" section, and the typical development workflow).

## Files to Look At

- `waspc/run` — main build script with command definitions and case dispatch
- `waspc/run.ps1` — PowerShell equivalent of the run script
- `.github/workflows/ci-waspc-build.yaml` — CI build workflow
- `waspc/README.md` — developer documentation referencing build commands
