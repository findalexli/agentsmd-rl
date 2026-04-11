# chore: refresh CLAUDE.md

## Problem

The Payload CMS repository's agent documentation needs to be refreshed and reorganized. Currently:

- `CLAUDE.md` is a symlink pointing to `AGENTS.md` (reverse of desired structure)
- `AGENTS.md` contains all the documentation but should be the symlink instead
- `.gitignore` is missing entries for new local AI agent files (`.claude/commands/*.local.md`, `.claude/artifacts`)

This structure is confusing and doesn't align with the standard practice of having `CLAUDE.md` as the primary file for Claude Code integration.

## Expected Behavior

1. **CLAUDE.md** should become the primary file with comprehensive documentation:
   - Project structure overview for the Payload monorepo
   - Key directories explanation (packages/, test/, docs/, tools/, templates/, examples/)
   - Architecture notes (Next.js native, RSC, Drizzle ORM, pnpm workspaces)
   - Build commands (`pnpm build`, `pnpm build:all`, `pnpm build:<dir>`)
   - Development server commands (`pnpm dev`, `pnpm dev:postgres`, `pnpm dev:memorydb`)
   - Testing instructions (integration, unit, e2e, component tests)
   - Linting and formatting commands
   - Internationalization workflow
   - Commit and PR guidelines with Conventional Commits format
   - Additional resources (LLMS.txt links, Node/pnpm version requirements)

2. **AGENTS.md** should become a symlink pointing to `CLAUDE.md` (reverse of current state)

3. **.gitignore** should be updated to include:
   - `.claude/commands/*.local.md` - local command files
   - `.claude/artifacts` - local artifacts directory

## Files to Look At

- `CLAUDE.md` - needs to be converted from symlink to full documentation file
- `AGENTS.md` - needs to be converted from full file to symlink
- `.gitignore` - needs new ignore patterns for local AI agent files
