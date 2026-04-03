# Set up Claude Code configuration for Payload

## Problem

The Payload repository lacks Claude Code configuration. There's no post-edit hook to automatically format files after edits, no permission presets to reduce repetitive approval prompts for common commands, and the `CLAUDE.md` documentation has several gaps and inconsistencies:

1. **No auto-formatting hook**: When Claude Code edits files, they don't get formatted with the project's tools (prettier, eslint, sort-package-json). This means edits may not match the project's formatting standards.

2. **No permission presets**: Every `git status`, `pnpm run test`, or `gh pr view` command requires manual approval, slowing down the workflow.

3. **CLAUDE.md documentation gaps**: The package listing is missing `packages/kv-redis` (Redis key-value store adapter) and doesn't mention the R2 storage adapter. Commands throughout the file use bare `pnpm build` / `pnpm dev` / `pnpm test` syntax instead of `pnpm run build` etc., and there's no guidance on using `pnpm turbo` instead of `turbo` directly. A Quick Start section is also missing.

## Expected Behavior

1. A post-edit hook (`.claude/hooks/post-edit.sh`) that automatically formats files after Edit/Write operations:
   - Sorts `package.json` files
   - Runs prettier on supported file types (yml, json, md, mdx, js, jsx, ts, tsx)
   - Runs eslint for JS/TS files
   - The hook should be robust — exit cleanly when given null input or nonexistent files

2. A `.claude/settings.json` that:
   - Configures the post-edit hook to trigger on Edit and Write tool use
   - Pre-allows common readonly commands (git, gh, pnpm) to reduce permission prompts

3. Updated `CLAUDE.md` that:
   - Lists all current packages including kv-redis and R2
   - Standardizes all pnpm commands to use `pnpm run` prefix
   - Includes guidance that Turbo commands should use `pnpm turbo`
   - Adds a Quick Start section

## Files to Look At

- `CLAUDE.md` — project documentation for Claude Code, needs updates
- `.claude/` — directory for Claude Code configuration (hooks, settings)
- `package.json` — check available scripts to understand the `pnpm run` prefix convention
- `packages/` — verify which packages exist (kv-redis, storage adapters)
