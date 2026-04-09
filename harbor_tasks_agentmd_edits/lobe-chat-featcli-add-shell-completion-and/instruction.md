# Add shell completion and migrate CLI bundler from tsup to tsdown

## Problem

The LobeHub CLI (`apps/cli`) currently uses `tsup` as its bundler. We want to:
1. Migrate the bundler from `tsup` to `tsdown`
2. Add interactive shell completion support for the `lh`/`lobe`/`lobehub` CLI commands

The shell completion should be context-aware (e.g., `lh agent <TAB>` should show agent subcommands instead of top-level commands).

## Expected Behavior

After the changes:

1. **Build migration**: `package.json` should use `tsdown` instead of `tsup` for the build script
2. **tsdown config**: A new `tsdown.config.ts` file should exist with proper configuration
3. **tsup removed**: The old `tsup.config.ts` should be removed
4. **Completion command**: A new `completion [shell]` command that outputs shell completion scripts for bash/zsh
5. **__complete command**: An internal `__complete` command (hidden) that returns completion candidates based on the current command context
6. **README updated**: `apps/cli/README.md` should document how to use shell completion
7. **Unit tests**: `apps/cli/src/commands/completion.test.ts` should test the completion functionality

## Files to Look At

- `apps/cli/package.json` — build script and dependencies
- `apps/cli/tsup.config.ts` — old bundler config (to be removed)
- `apps/cli/src/index.ts` — CLI entry point where commands are registered
- `apps/cli/src/commands/` — directory for command implementations
- `apps/cli/src/utils/` — utility functions
- `apps/cli/README.md` — documentation (needs update)

## Files to Create

- `apps/cli/tsdown.config.ts` — new bundler configuration
- `apps/cli/src/commands/completion.ts` — completion command implementation
- `apps/cli/src/commands/completion.test.ts` — unit tests
- `apps/cli/src/utils/completion.ts` — completion utility functions
- `apps/cli/README.md` — documentation (if doesn't exist, or update existing)

## Implementation Notes

The completion system consists of:

1. **`completion [shell]` command**: Outputs a shell script for the specified shell (bash/zsh). If no shell is specified, it should detect from `$SHELL` environment variable.

2. **`__complete [words...]` command** (hidden): This is called by the shell completion scripts to get candidates. It should:
   - Read `LOBEHUB_COMP_CWORD` environment variable to know which word is being completed
   - Parse the command context (e.g., `lh agent list` means we're in the `agent` subcommand context)
   - Return completion candidates (commands, subcommands, or options) one per line

3. **Utility functions** (`src/utils/completion.ts`):
   - `getCompletionCandidates(program, words, currentWordIndex)` — returns list of candidates
   - `resolveCompletionShell(shell?)` — resolves shell name from arg or env
   - `renderCompletionScript(shell)` — generates bash/zsh completion script
   - `parseCompletionWordIndex(raw, words)` — parses LOBEHUB_COMP_CWORD

The completion should:
- Only show visible commands (not hidden ones like `__complete`)
- Be context-aware (suggest subcommands in nested contexts)
- Suggest options after leaf commands
- Filter candidates based on the current word being typed
