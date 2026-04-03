# Upgrade Prisma from 5.4.1 to 6.14.0

## Problem

The `@trigger.dev/database` internal package uses Prisma 5.4.1 which is outdated. Prisma 6 introduced breaking changes that require migrating the generated client output location and updating import paths throughout the codebase.

Currently:
- `internal-packages/database/prisma/schema.prisma` generates the Prisma client in the default location and uses the deprecated `"tracing"` preview feature
- `internal-packages/database/src/index.ts` re-exports from `@prisma/client` directly
- `internal-packages/database/src/transaction.ts` imports types from `@prisma/client` using the `Prisma` namespace (e.g., `Prisma.Decimal`, `Prisma.TransactionIsolationLevel`, `Prisma.PrismaClientKnownRequestError`)
- The webapp lacks query performance monitoring for detecting slow database queries

## Expected Behavior

After the upgrade:
1. The Prisma schema should generate the client to a `generated/prisma` directory under the database package, and the deprecated `"tracing"` preview feature should be removed
2. All imports/exports should reference the new generated output path instead of `@prisma/client` directly
3. Types that were previously accessed through the `Prisma` namespace (like `Decimal`, `TransactionIsolationLevel`, `PrismaClientKnownRequestError`) should be imported from their proper sources (`decimal.js`, `@prisma/client/runtime/library`, or defined locally)
4. A query performance monitor should be added to the webapp that logs very slow queries (controlled by a new `VERY_SLOW_QUERY_THRESHOLD_MS` environment variable)
5. The project's agent configuration files should be updated to reflect the new Prisma version

## Files to Look At

- `internal-packages/database/prisma/schema.prisma` — Prisma schema with generator config
- `internal-packages/database/src/index.ts` — re-exports the Prisma client
- `internal-packages/database/src/transaction.ts` — transaction utilities using Prisma types
- `internal-packages/database/package.json` — dependency versions
- `apps/webapp/app/env.server.ts` — environment variable definitions
- `apps/webapp/app/db.server.ts` — Prisma client setup
- `.cursor/rules/webapp.mdc` — agent configuration referencing Prisma version
