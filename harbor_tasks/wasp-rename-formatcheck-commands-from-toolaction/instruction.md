# Rename format/check commands to action:tool convention

## Problem

The project's `run` script uses an inconsistent naming convention for its formatting and checking commands. Commands are currently named as `tool:action` (e.g., `ormolu:check`, `prettier:format`, `cabal-gild:format`), but the project wants to follow a more intuitive `action:tool` convention where the action verb comes first (e.g., `check:ormolu`, `format:prettier`).

Additionally, there are no top-level `format` or `check` commands that run all formatters/checkers at once — developers must run each tool individually.

## Expected Behavior

1. All formatting/checking commands should follow the `action:tool` pattern:
   - `format:ormolu`, `check:ormolu` (instead of `ormolu:format`, `ormolu:check`)
   - `format:cabal`, `check:cabal` (instead of `cabal-gild:format`, `cabal-gild:check`)
   - `format:prettier`, `check:prettier` (instead of `prettier:format`, `prettier:check`)

2. New top-level `format` and `check` commands should be added that run all formatters/checkers together.

3. All references to the old command names across the project — including npm scripts, CI workflows, and documentation — should be updated to use the new naming convention.
