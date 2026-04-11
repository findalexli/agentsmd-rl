# Set up Claude Code configuration with sane defaults

## Problem

The Payload CMS repository is missing Claude Code integration configuration. There are no post-edit hooks to automatically format files after edits, no permissions presets to reduce prompts for common read-only commands, and the `CLAUDE.md` documentation is incomplete and inconsistent.

Specifically:
- No `.claude/hooks/` directory or formatting hooks exist — files edited by Claude Code don't get auto-formatted
- No `.claude/settings.json` exists — every git/pnpm command triggers a permission prompt
- `CLAUDE.md` is missing documentation for some packages (`kv-redis`, R2 storage adapter)
- `CLAUDE.md` has no Quick Start section for new contributors
- pnpm commands in `CLAUDE.md` use inconsistent formats — some use bare `pnpm build` while the monorepo's permission rules require `pnpm run build`
- No guidance about running Turbo commands through pnpm rather than directly

## Expected Behavior

1. **Post-edit hook** (`.claude/hooks/post-edit.sh`): A bash script that auto-formats files after Edit/Write operations. It should read JSON from stdin to get the file path, then run the appropriate formatter based on file type (prettier for most files, sort-package-json for package.json, eslint for JS/TS files, markdownlint for markdown).

2. **Settings** (`.claude/settings.json`): Configure the post-edit hook to trigger on Edit and Write tool use. Set up a permissions allowlist for common read-only commands (git, gh, pnpm) and web fetching from relevant domains.

3. **CLAUDE.md updates**: Add missing packages to the key directories listing, add a Quick Start section, standardize all pnpm commands to use `pnpm run` prefix (matching what the permissions allow), and add a note about using `pnpm turbo` instead of bare `turbo`.

## Files to Look At

- `.claude/hooks/post-edit.sh` — new hook script for auto-formatting
- `.claude/settings.json` — new settings with hooks and permissions
- `CLAUDE.md` — existing documentation that needs updates
