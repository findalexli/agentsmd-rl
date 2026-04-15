# Remove obsolete setup.js script and update documentation

## Repository Context

This is the Ghost CMS repository at commit `c1e86e6`. The repository contains:
- `.github/scripts/` with helper scripts including `bump-version.js`
- `.github/hooks/pre-commit` and `.github/hooks/commit-msg` git hooks
- `.github/workflows/ci.yml` with jobs: `job_setup:`, `job_lint:`, `job_unit-tests:`
- `docs/README.md` with a "Quick Start" section describing Ghost development setup
- `package.json` with a `setup` script
- `Dockerfile` for containerized deployment

## Problem

The `.github/scripts/setup.js` script is obsolete. It was originally responsible for:
- Setting up MySQL via Docker
- Writing `config.local.json` during `yarn setup`
- Setting up git hooks

However, `yarn dev` now handles Docker backend service setup automatically (MySQL, Redis, Mailpit, Caddy). The setup.js script is now dead code but is still referenced.

### Issues caused by this:

1. **Dead code still invoked**: The `setup` script in `package.json` invokes `node .github/scripts/setup.js`, but this script no longer needs to perform its original MySQL/config setup duties.

2. **Missing `--recursive` flag**: The current setup script runs `git submodule update --init` without the `--recursive` flag, which is needed for nested submodules.

3. **Outdated documentation in `docs/README.md`**: The contributor documentation describes the old workflow:
   - Says setup "initializes the database" and "sets up git hooks" — this is no longer accurate
   - Describes `yarn dev` as "Start development server (uses Docker for backend services)" but doesn't mention that it now also starts frontend dev servers
   - Instructs users to run `yarn knex-migrator reset` and `yarn knex-migrator init` for database reset, but the current workflow uses `yarn reset:data`

## Expected Behavior

1. **`.github/scripts/setup.js`** should no longer exist — it is dead code that performed MySQL Docker setup and config writing now handled by `yarn dev`.

2. **`package.json` setup script** should:
   - NOT reference `setup.js` or run arbitrary Node.js scripts
   - Use `--recursive` flag for `git submodule update --init`
   - Consist of exactly two parts: dependency installation (`yarn`) and submodule initialization (`git submodule update --init --recursive`)

3. **`docs/README.md`** should be updated to reflect the current development workflow:
   - The setup section should NOT mention "initializes the database" or "sets up git hooks"
   - The setup section should describe installing dependencies and initializing submodules
   - The `yarn dev` description should mention frontend dev servers (not just Docker backend services)
   - The reset instructions should use `yarn reset:data` instead of `yarn knex-migrator reset` and `yarn knex-migrator init`

## Files to Look At

- `.github/scripts/setup.js` — the obsolete setup script
- `package.json` — contains the `setup` script definition
- `docs/README.md` — contributor documentation describing setup and development workflow
