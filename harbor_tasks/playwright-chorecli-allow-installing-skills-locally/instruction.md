# chore(cli): allow installing skills locally

## Problem

The Playwright CLI lacks a command to install skill files to the local workspace. Users need a way to copy skill documentation and reference files for integration with Claude and GitHub Copilot.

Additionally:
- The `install` command is ambiguously named
- Route tools (`browser_route`, `browser_route_list`, `browser_unroute`) are categorized under `core` capability, but should be under `network`
- The `--isolated` flag has been renamed to `--in-memory`, but the help text hasn't been updated

## Expected Behavior

1. An `install-skills` CLI command exists that copies skill files to `.claude/skills/playwright/` in the current working directory
2. When run, it prints "Skills installed to" followed by a relative path
3. The command copies the `references` subdirectory alongside other skill files
4. The existing `install` command is renamed to `install-browser` for clarity
5. Route tools use the `network` capability instead of `core`
6. The `network` capability is added to the config type definitions
7. The help text shows `--in-memory` instead of `--isolated`

## Verification Criteria

The `packages/playwright/src/skill/SKILL.md` file must:
- Exist and be a valid skill documentation file
- Contain a `name:` field
- Contain the string `playwright-cli`

The `install-skills` command must:
- Appear in `--help` output
- Copy files to `.claude/skills/playwright/` including a `references/` subdirectory

TypeScript compilation must pass without errors.