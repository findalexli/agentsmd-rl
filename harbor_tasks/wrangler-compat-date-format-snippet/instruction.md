# Compatibility date warning shows wrong config format for JSON users

## Problem

When running `wrangler dev` without a `compatibility_date` set, the CLI prints a warning suggesting the user add one to their config file. The suggested config snippet is always shown in TOML format (`compatibility_date = "2025-01-01"`), even when the user's config file is `wrangler.json` or `wrangler.jsonc`. This is confusing because the TOML syntax is invalid in a JSON config file.

## Expected Behavior

The compatibility date suggestion in the warning should render in the correct format based on the user's config file type — TOML format for `wrangler.toml`, JSON format for `wrangler.json`/`wrangler.jsonc`.

## Files to Look At

- `packages/wrangler/src/api/startDevWorker/ConfigController.ts` — contains the `getDevCompatibilityDate` function that produces the warning message
- `packages/workers-utils/src/config/index.ts` — contains utility functions for config format handling
