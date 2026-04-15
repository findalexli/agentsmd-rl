# Migrate @cypress/grep from Cypress.env() to Cypress.expose()

## Problem

`Cypress.env()` is deprecated as of Cypress 15.10.0. The `@cypress/grep` plugin currently uses `Cypress.env()` throughout its codebase to read and write grep filter configuration. This needs to be migrated to the new `Cypress.expose()` API.

The plugin has two main entry points that need updating:
- **`npm/grep/src/plugin.ts`** — the Node-side plugin that reads config and pre-filters spec files
- **`npm/grep/src/register.ts`** — the browser-side support file registration that reads config and filters tests at runtime

## Expected Behavior

After the migration:

1. **Plugin reads from config.expose**: The `plugin()` function must read grep filter configuration from `config.expose` instead of `config.env`. The grep configuration includes these keys: `grep`, `grepTags`, `grepBurn`, `grepFilterSpecs`, `grepOmitFiltered`, `grepUntagged`, `grepIntegrationFolder`, `burn`, `grep-tags`, `grep-burn`, `grep-omit-filtered`, `grep-untagged`. When only `config.env` is present (old API), the plugin must return the config unchanged (no-op). When `config.expose` is present, the plugin must process the grep configuration and log grep patterns to console.

2. **Support file uses Cypress.expose()**: The file `npm/grep/src/register.ts` must contain the literal string `Cypress.expose(` and must not contain the literal string `Cypress.env(`. All get/set operations for grep configuration must use the new `Cypress.expose()` API.

3. **Peer dependency updated**: The `npm/grep/package.json` peerDependencies.cypress field must require version `>=15.10.0` (e.g., `">=15.10.0"` or a range that satisfies this minimum).

4. **npm scripts use --expose**: All npm scripts in `npm/grep/package.json` that invoke `cypress` and contain grep-related terms (grep, burn, Tags, Untagged) must use the literal string `--expose` instead of `--env` for passing grep arguments.

5. **README updated**: The `npm/grep/README.md` must be updated to reflect the new API:
   - All CLI examples must use the literal string `--expose` instead of `--env`
   - All configuration examples must use the literal key `expose:` instead of `env:`
   - A migration guide section titled exactly "Migrating from v5 to v6" must be added for users upgrading from v5 to v6

## Files to Modify

- `npm/grep/src/plugin.ts` — Node-side plugin, change `config.env` to `config.expose`
- `npm/grep/src/register.ts` — Browser-side registration, change `Cypress.env(` to `Cypress.expose(`
- `npm/grep/package.json` — Update scripts to use `--expose` and peerDependencies.cypress to `>=15.10.0`
- `npm/grep/README.md` — Update all CLI examples to use `--expose`, config examples to use `expose:`, and add "Migrating from v5 to v6" section
