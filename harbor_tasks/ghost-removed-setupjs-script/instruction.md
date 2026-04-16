# Remove obsolete setup.js script and update documentation

## Repository Context

This is the Ghost CMS repository at commit `c1e86e6`. The repository contains:
- `.github/scripts/` with helper scripts including `bump-version.js`, `install-deps.sh`, `clean.js`, and `dependency-inspector.js`
- `.github/hooks/pre-commit` and `.github/hooks/commit-msg` git hooks
- `.github/workflows/ci.yml` with jobs: `job_setup:`, `job_lint:`, `job_unit-tests:`
- `docs/README.md` with a "Quick Start" section describing Ghost development setup
- `package.json` with a `setup` script that currently references `setup.js`
- `ghost/core/package.json` with name field equal to `ghost`
- `Dockerfile` for containerized deployment

## Problem

The `.github/scripts/setup.js` script is obsolete. It was originally responsible for:
- Setting up MySQL via Docker
- Writing `config.local.json` during `yarn setup`
- Setting up git hooks

However, `yarn dev` now handles Docker backend service setup automatically (MySQL, Redis, Mailpit, Caddy). The setup.js script is now dead code but is still referenced in package.json.

### Issues caused by this:

1. **Dead code still invoked**: The `setup` script in `package.json` invokes `node .github/scripts/setup.js`, but this script no longer needs to perform its original MySQL/config setup duties.

2. **Missing `--recursive` flag**: The current setup script runs `git submodule update --init` without the `--recursive` flag, which is needed for nested submodules.

3. **Outdated documentation in `docs/README.md`**: The contributor documentation describes the old workflow:
   - Says setup "initializes the database" and "sets up git hooks" — this is no longer accurate since `yarn dev` handles these automatically
   - Describes `yarn dev` with text "Start development server (uses Docker for backend services)" but doesn't mention that it now also starts frontend dev servers
   - Instructs users to run `yarn knex-migrator reset` and `yarn knex-migrator init` for database reset, but the current workflow uses `yarn reset:data` instead

## Expected Behavior

1. The file `.github/scripts/setup.js` should no longer exist — it is dead code that performed MySQL Docker setup and config writing now handled by `yarn dev`.

2. The `package.json` setup script should be simplified to only handle dependency installation and submodule initialization. It should not reference `setup.js` or run arbitrary Node.js scripts, and should use the `--recursive` flag for `git submodule update --init`.

3. The `docs/README.md` should be updated to reflect the current development workflow:
   - The setup section should NOT mention "initializes the database" or "sets up git hooks" (these are now handled automatically by `yarn dev`)
   - The setup section should describe installing dependencies and initializing submodules (phrase "Install dependencies and initialize submodules" should be present)
   - The `yarn dev` description should mention frontend dev servers (phrase "frontend dev servers" should be present) and should not contain the old text "Start development server (uses Docker for backend services)"
   - The reset instructions should use `yarn reset:data` instead of `yarn knex-migrator reset` and `yarn knex-migrator init`
