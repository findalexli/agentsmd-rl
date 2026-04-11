# Remove obsolete setup.js script

## Problem

The `.github/scripts/setup.js` script is no longer needed. It was originally responsible for setting up MySQL via Docker and writing `config.local.json` during `yarn setup`. However, the `yarn dev` command now handles Docker backend service setup (MySQL, Redis, Mailpit, Caddy) automatically.

As a result:
- The `setup` script in `package.json` still invokes `setup.js`, which is now dead code
- The setup script is missing `--recursive` for `git submodule update --init`, which is needed for nested submodules
- The contributor documentation in `docs/README.md` describes the old workflow (setup initializes the database, manual `knex-migrator` commands for reset) which is no longer accurate

## Expected Behavior

- `.github/scripts/setup.js` should be removed
- The `setup` script in `package.json` should be simplified to just install dependencies and initialize submodules (with `--recursive`)
- `docs/README.md` should be updated to accurately reflect the current development workflow — setup no longer touches the database, `yarn dev` starts both backend services and frontend dev servers, and database reset uses a different command

## Files to Look At

- `.github/scripts/setup.js` — the obsolete setup script to remove
- `package.json` — contains the `setup` script definition
- `docs/README.md` — contributor documentation describing setup and development workflow
