# Rename format/check commands to action:tool convention

## Problem

The `waspc/run` script uses an inconsistent naming convention for its formatting and checking commands. Commands are currently named as `tool:action` (e.g., `ormolu:check`, `prettier:format`, `cabal-gild:format`), but the project wants to follow a more intuitive `action:tool` convention where the action verb comes first (e.g., `check:ormolu`, `format:prettier`).

Additionally, there are no top-level `format` or `check` commands that run all formatters/checkers at once — developers must run each tool individually.

## Expected Behavior

1. All formatting/checking commands in the `run` script should follow the `action:tool` pattern:
   - `format:ormolu`, `check:ormolu` (instead of `ormolu:format`, `ormolu:check`)
   - `format:cabal`, `check:cabal` (instead of `cabal-gild:format`, `cabal-gild:check`)
   - `format:prettier`, `check:prettier` (instead of `prettier:format`, `prettier:check`)

2. New top-level `format` and `check` commands that run all formatters/checkers together.

3. The npm scripts in `package.json` and CI workflow should be updated to match.

4. After making the code changes, update the relevant documentation to reflect the new command names. The project README under `waspc/` references the old command names in its formatting section.

## Files to Look At

- `waspc/run` — the main build/dev script with command definitions and case dispatch
- `package.json` — npm scripts for prettier
- `.github/workflows/ci-formatting.yaml` — CI pipeline that runs the formatter check
- `waspc/README.md` — developer documentation that references run script commands
