# Migrate @cypress/grep from Cypress.env() to Cypress.expose()

## Problem

`Cypress.env()` is deprecated as of Cypress 15.10.0. The `@cypress/grep` plugin currently uses `Cypress.env()` throughout its codebase to read and write grep filter configuration (grep patterns, tags, burn count, etc.). This needs to be migrated to the new `Cypress.expose()` API.

The plugin has two main entry points that need updating:
- **`npm/grep/src/plugin.ts`** — the Node-side plugin that reads config and pre-filters spec files
- **`npm/grep/src/register.ts`** — the browser-side support file registration that reads config and filters tests at runtime

Both files read grep configuration values (grep, grepTags, grepBurn, grepFilterSpecs, etc.) from `Cypress.env()` / `config.env` and need to be updated to use `Cypress.expose()` / `config.expose`.

## Expected Behavior

After the migration:
1. The plugin reads filter config from `config.expose` instead of `config.env`
2. The support file registration uses `Cypress.expose()` instead of `Cypress.env()` for all get/set operations
3. The `package.json` peer dependency is updated to require Cypress `>=15.10.0`
4. The `package.json` npm scripts use `--expose` instead of `--env` for passing grep arguments
5. The plugin's README is updated to reflect the new API — all CLI examples, configuration examples, and relevant documentation should use `--expose` / `expose:` instead of `--env` / `env:`. A migration guide section should be added for users upgrading from v5 to v6.

## Files to Look At

- `npm/grep/src/plugin.ts` — Node-side plugin, reads from config object
- `npm/grep/src/register.ts` — Browser-side registration, uses Cypress API directly
- `npm/grep/package.json` — Scripts and peer dependency
- `npm/grep/README.md` — User-facing documentation with CLI examples and config examples
- `npm/grep/cypress.config.ts` — The plugin's own test config
- `npm/grep/cypress/e2e/grep-task.cy.ts` — E2E test file using the plugin
