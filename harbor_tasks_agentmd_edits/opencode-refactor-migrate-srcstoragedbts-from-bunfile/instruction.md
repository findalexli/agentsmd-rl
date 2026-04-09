# Refactor: migrate src/storage/db.ts from Bun.file() to statSync

## Problem

The `migrations()` function in `packages/opencode/src/storage/db.ts` currently uses `Bun.file(file).size` to check if a migration SQL file exists before reading it. This is problematic because:

1. `Bun.file(file).size` returns 0 for non-existent files (or may throw in some Bun versions), which is semantically incorrect for an existence check
2. The codebase is migrating away from Bun-specific APIs toward standard Node.js `fs` module functions for better compatibility
3. The existing pattern is less clear than using an explicit `existsSync()` check

## Expected Behavior

1. **Update imports**: Add `existsSync` to the import from the `fs` module
2. **Replace existence check**: Change `if (!Bun.file(file).size) return` to `if (!existsSync(file)) return`
3. **Remove obsolete skill file**: The `.opencode/skill/bun-file-io/SKILL.md` file documents Bun.file() patterns that are being phased out - this file should be removed as part of this migration

## Files to Look At

- `packages/opencode/src/storage/db.ts` — The main file to modify (around line 57 in the `migrations()` function)
- `.opencode/skill/bun-file-io/SKILL.md` — Remove this file entirely

## Implementation Notes

The `migrations()` function iterates over directories looking for `migration.sql` files. The fix changes how we detect missing files:
- **Before**: `if (!Bun.file(file).size) return` — Relies on Bun-specific behavior
- **After**: `if (!existsSync(file)) return` — Uses standard Node.js fs.existsSync

Both approaches skip directories without a migration.sql file, but the Node.js approach is clearer and more portable.
