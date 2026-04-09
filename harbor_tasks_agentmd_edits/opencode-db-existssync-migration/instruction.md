# Migrate storage/db.ts from Bun.file() to Node.js fs module

## Problem

The codebase is migrating away from Bun-specific file APIs toward Node.js standard library for better compatibility. The `packages/opencode/src/storage/db.ts` file currently uses `Bun.file(file).size` to check if migration SQL files exist. This needs to be replaced with the standard Node.js `existsSync` function.

Additionally, there's an outdated skill file `.opencode/skill/bun-file-io/SKILL.md` that documents the old Bun file API patterns. Since we're moving away from these patterns, this documentation file should be removed as part of the migration.

## Expected Behavior

1. `packages/opencode/src/storage/db.ts` should:
   - Import `existsSync` from the `fs` module (alongside existing `readFileSync` and `readdirSync` imports)
   - Replace `Bun.file(file).size` with `existsSync(file)` for checking migration file existence

2. The `.opencode/skill/bun-file-io/SKILL.md` file should be deleted entirely

## Files to Look At

- `packages/opencode/src/storage/db.ts` — Database migration logic that checks for migration.sql files
- `.opencode/skill/bun-file-io/SKILL.md` — Outdated skill documentation for Bun file APIs (to be deleted)

## Notes

- This is part of a broader migration effort to reduce Bun-specific API usage
- The `migrations()` function in db.ts reads migration files from subdirectories
- Focus on the change in the `dirs.map()` logic where file existence is checked
