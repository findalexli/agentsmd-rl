# CLI session commands need shorter names and a -b flag alias

## Problem

The `playwright-cli` session management commands have verbose, `session-`-prefixed names (`session-list`, `session-close-all`, `session-kill-all`) and the `--session` flag is unnecessarily long for frequent use. The session-related terminology is also inconsistent — internally these manage browser instances, but the CLI uses "session" terminology throughout user-facing messages and documentation.

The commands should be shortened to `list`, `close-all`, and `kill-all`. The `--session` flag should get a short `-b` alias. User-facing messages should use "Browser" terminology instead of "Session" (e.g., "Browser 'default' closed" instead of "Session 'default' stopped"), and status markers should say `[open]`/`[closed]` instead of `[running]`/`[stopped]`.

## Expected Behavior

- `playwright-cli list` lists browser sessions (was `session-list`)
- `playwright-cli close-all` closes all sessions (was `session-close-all`)
- `playwright-cli kill-all` force-kills all daemons (was `session-kill-all`)
- `playwright-cli -b mysession open ...` works as a short alias for `--session`
- The `session` category is renamed to `browsers`
- All user-facing console output says "Browser" instead of "Session"
- Status markers show `[open]`/`[closed]` instead of `[running]`/`[stopped]`

## Files to Look At

- `packages/playwright/src/mcp/terminal/command.ts` — defines the `Category` type union
- `packages/playwright/src/mcp/terminal/commands.ts` — declares session commands with names and categories
- `packages/playwright/src/mcp/terminal/helpGenerator.ts` — generates CLI help text
- `packages/playwright/src/mcp/terminal/program.ts` — implements command dispatch, session management, and user-facing messages

After making the code changes, update the CLI skill documentation and references to reflect the new command names and `-b` flag. The project's dev skill file (`.claude/skills/playwright-mcp-dev/SKILL.md`) says to update the skill file and references when commands change.

- `packages/playwright/src/skill/SKILL.md` — documents all CLI commands including session management
- `packages/playwright/src/skill/references/session-management.md` — detailed session management reference documentation

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
