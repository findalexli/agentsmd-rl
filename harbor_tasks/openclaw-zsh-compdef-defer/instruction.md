# fix(cli): defer zsh compdef registration until compinit is available

## Problem

The generated zsh completion script calls `compdef` at source time, which fails with `command not found: compdef` when the script is loaded before `compinit` runs. This happens in most plugin manager setups and manual configurations where the completion script is sourced before compinit.

## Symptom

```
command not found: compdef
```

## Expected Behavior

The zsh completion registration must succeed regardless of whether `compinit` has run when the script is sourced. Specifically:

1. **Availability check**: Before calling `compdef`, the script must verify that `compdef` is available (using any of: `whence compdef`, `type compdef`, `command -v compdef`, `whence -w compdef`, or `(( $+functions[compdef] ))`)
2. **Deferred registration**: If `compdef` is not available at source time, the registration must be retried after the first prompt via `precmd_functions`
3. **Cleanup**: After `compdef` succeeds, the registration hook must remove itself from the hook array and undefine itself so it does not run again
4. **No duplicate hooks**: Repeated sourcing of the script must not add duplicate entries to `precmd_functions`
5. **Root completion function intact**: The `_root_completion` function definition (containing `case`, `compadd`, or `_arguments`) must remain in the generated script

## Files to Modify

- `src/cli/completion-cli.ts`
