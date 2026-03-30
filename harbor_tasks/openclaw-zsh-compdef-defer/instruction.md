# fix(cli): defer zsh compdef registration until compinit is available

## Problem

The generated zsh completion script calls `compdef` at source time, which fails with `command not found: compdef` when the script is loaded before `compinit` runs. This happens in most plugin manager setups and manual configurations where the completion script is sourced before compinit.

## Root Cause

`getCompletionScript('zsh')` in `src/cli/completion-cli.ts` emits a bare `compdef _openclaw_root_completion openclaw` at the top level. This runs at source time, before `compinit` has been called in most plugin manager and manual setups.

## Expected Fix

Replace the bare `compdef` call with deferred registration:
1. Define a `_openclaw_register_completion()` function that:
   - Checks if `compdef` is available (using `(( $+functions[compdef] ))`)
   - If available, calls `compdef`, then removes itself from `precmd_functions` and undefines itself
   - If not available, returns 0 (no-op)
2. Try calling the registration function immediately
3. If `compdef` was not available, queue the function in `precmd_functions` so it retries on the first prompt
4. Handle repeated sourcing (deduped hook entry) and shells that never run `compinit`

## Files to Modify

- `src/cli/completion-cli.ts`
