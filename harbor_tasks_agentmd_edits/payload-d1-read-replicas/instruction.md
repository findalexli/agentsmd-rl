# Add Read Replicas Support to D1 SQLite Adapter

## Problem

The Payload CMS D1 SQLite adapter (`@payloadcms/db-d1-sqlite`) does not support Cloudflare D1's read replicas feature. Cloudflare D1 supports a `first-primary` read replication strategy via the `withSession` API, but there is no way to enable this through the adapter's configuration.

Users who want to improve read query performance by leveraging D1 read replicas have no way to do so through the adapter config — they would need to manually patch the adapter's connection logic.

## Expected Behavior

1. The adapter should accept a `readReplicas` option (accepting the `'first-primary'` strategy) in its configuration.
2. When `readReplicas` is set, the adapter's connect logic should use the D1 `withSession` API to enable read replication on the binding before passing it to Drizzle.
3. The type definitions should be updated for both the `Args` input type and the `SQLiteD1Adapter` type to include the new option.
4. The adapter factory in `index.ts` must pass the option through from args to the adapter instance.

After implementing the code changes, update the relevant documentation to reflect the new feature:
- The database documentation should describe how to enable D1 read replicas, including a code example.
- The Cloudflare D1 template README should mention the read replicas option and note the Paid Workers deployment requirement.

## Files to Look At

- `packages/db-d1-sqlite/src/types.ts` — Type definitions for adapter args and the adapter itself
- `packages/db-d1-sqlite/src/connect.ts` — Connection logic where the D1 binding is initialized
- `packages/db-d1-sqlite/src/index.ts` — Adapter factory function that wires args to the adapter
- `docs/database/sqlite.mdx` — Database documentation covering SQLite and D1 adapters
- `templates/with-cloudflare-d1/README.md` — Template README for the Cloudflare D1 example
