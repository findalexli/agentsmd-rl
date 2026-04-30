# Replace external slimer tool with in-repo migration scaffolding

## Problem

Ghost's database migration scaffolding currently depends on `slimer`, an external package invoked as `slimer migration <name>`. This tool doesn't understand Ghost's RC versioning convention — when Ghost is at a stable version like `6.18.0`, the first new migration should target folder `6.19` and bump `package.json` to `6.19.0-rc.0`. `slimer` doesn't handle this, so developers must manually create version directories and bump versions.

## What needs to happen

Create an in-repo Node.js script at `ghost/core/bin/create-migration.js` that replaces `slimer` for migration file creation. The script should:

- Accept a **kebab-case slug** (e.g., `add-column-to-posts`) and validate it
- Calculate the correct migration version folder from the current `package.json` version, using `semver` (already a dependency). The key invariant: both a stable release (e.g., `6.18.0`) and its corresponding RC (e.g., `6.19.0-rc.0`) should target the **same** migration folder (`6.19`)
- Create a timestamped migration file (e.g., `2026-02-23-10-30-00-add-column.js`) with a standard template
- Create the version directory if it doesn't already exist
- Auto-bump `ghost/core/package.json` (and `ghost/admin/package.json` if it exists) to RC when the current version is stable — but skip the bump if already on a prerelease
- Export the core functions (`isValidSlug`, `getNextMigrationVersion`, `createMigration`) for testability, with a CLI entry point when run directly

Wire it up as `yarn migrate:create` in `ghost/core/package.json`.

## Don't forget the agent instructions

The project has a Claude skill file at `.claude/skills/create-database-migration/SKILL.md` that currently documents the old `slimer`-based workflow. This file needs to be updated to reflect the new `yarn migrate:create` command, including the kebab-case slug requirement and the automatic RC version bumping behavior.

## Files to look at

- `ghost/core/package.json` — add the new script entry
- `ghost/core/bin/` — where other Ghost CLI scripts live
- `.claude/skills/create-database-migration/SKILL.md` — agent instructions for migration creation
