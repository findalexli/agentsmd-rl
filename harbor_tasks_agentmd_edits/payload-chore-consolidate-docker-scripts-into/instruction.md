# Consolidate Docker Scripts into Unified Docker Compose with Profiles

## Problem

The monorepo currently has **18 separate docker scripts** in `package.json` and **4 separate docker-compose files** spread across different directories (`test/__helpers/shared/db/postgres/`, `test/__helpers/shared/db/mongodb/`, `test/__helpers/shared/db/mongodb-atlas/`, `packages/storage-s3/`). Each database has its own `start`, `stop`, `restart`, and `restart:clean` commands. This is confusing — developers have to hunt through `package.json` to find the right `docker:mongodb:start` or `docker:postgres:restart:clean` command.

Meanwhile, `test/docker-compose.yml` already exists but only defines the storage emulators (LocalStack, Azure, GCS) without any profiles.

## Expected Behavior

Replace all per-database docker scripts and separate compose files with:

1. **One unified `test/docker-compose.yml`** using Docker Compose profiles (`postgres`, `mongodb`, `mongodb-atlas`, `storage`, `all`) so all services are defined in a single file
2. **Three simple scripts** in `package.json`:
   - `docker:start` — tears down old volumes and starts all services fresh
   - `docker:stop` — stops everything
   - `docker:test` — tests database connections
3. **CI updated** to use the unified compose file with `--profile` flags instead of per-database compose file paths

The old per-database docker-compose files should be removed since their service definitions are now in the unified file.

After making the code changes, update the project's documentation (`CLAUDE.md`, `CONTRIBUTING.md`) to reflect the new simplified Docker workflow. The current docs reference old per-database commands that will no longer exist.

## Files to Look At

- `package.json` — current docker scripts (lines 85-106)
- `test/docker-compose.yml` — existing compose file to extend with all services and profiles
- `test/__helpers/shared/db/*/docker-compose.yml` — per-database compose files to consolidate
- `packages/storage-s3/docker-compose.yml` — storage compose file to consolidate
- `.github/actions/start-database/action.yml` — CI action that starts databases
- `CLAUDE.md` — agent instructions referencing docker commands
- `CONTRIBUTING.md` — contributor docs with docker setup instructions
