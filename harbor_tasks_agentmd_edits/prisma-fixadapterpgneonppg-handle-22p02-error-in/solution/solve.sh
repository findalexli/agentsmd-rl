#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

# Idempotent: skip if already applied
if grep -q 'InvalidInputValue' packages/driver-adapter-utils/src/types.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index 54a9699c7f47..b6bf8a7e96a9 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -8,6 +8,17 @@
 - **Driver adapters & runtimes**: `packages/bundled-js-drivers` plus the `adapter-*` packages ship experimental JS driver adapters (Planetscale, Neon, libsql, D1, etc.) built on helpers in `driver-adapter-utils`; migrate/client fixtures exercise them, so adapter changes typically require fixture/test updates.
 - **Build & tooling**: Typescript-first repo with WASM/Rust assets (downloaded by `@prisma/engines`). Multiple `tsconfig.*` drive bundle vs runtime builds. Lint via `pnpm lint`, format via `pnpm format`. Maintenance scripts live in `scripts/` (e.g. `bump-engines.ts`, `bench.ts`, `ci/publish.ts` orchestrates build/test/publish flows). Build configuration uses esbuild via `helpers/compile/build.ts` with configs in `helpers/compile/configs.ts`. Most packages use `adapterConfig` which bundles to both CJS and ESM with type declarations.
 - **Testing & databases**: `TESTING.md` covers Jest/Vitest usage. Most suites run as `pnpm --filter @prisma/<pkg> test <pattern>`. DB-backed tests expect `.db.env` and Docker services from `docker/docker-compose.yml` (`docker compose up -d`). Client functional tests sit in `packages/client/tests/functional`—run them via `pnpm --filter @prisma/client test:functional` (with typechecking) or `pnpm --filter @prisma/client test:functional:code` (code only); `helpers/functional-test/run-tests.ts` documents CLI flags to target providers, drivers, etc. Client e2e suites require a fresh `pnpm build` at repo root, then `pnpm --filter @prisma/client test:e2e --verbose --runInBand`. The legacy `pnpm --filter @prisma/client test` command primarily runs the older Jest unit tests plus `tsd` type checks. Migrate CLI suites live in `packages/migrate/src/__tests__`, the CLI runs both Jest (legacy suites) and Vitest (new subcommand coverage) via `pnpm --filter prisma test`, and end-to-end coverage lives in `packages/integration-tests`.
+
+- **Client functional tests structure**:
+  - Each test lives in its own folder under `packages/client/tests/functional/` (or `issues/` for regression tests).
+  - Required files: `_matrix.ts` (test configurations), `test.ts` or `tests.ts` (test code), `prisma/_schema.ts` (schema template).
+  - `_matrix.ts` defines provider/adapter combinations using `defineMatrix(() => [[{provider: Providers.POSTGRESQL}, ...]])`.
+  - `prisma/_schema.ts` exports `testMatrix.setupSchema(({ provider }) => ...)` returning a Prisma schema string.
+  - Test file uses `testMatrix.setupTestSuite(() => { test(...) }, { optOut: { from: [...], reason: '...' } })`.
+  - Run specific adapter: `pnpm --filter @prisma/client test:functional:code --adapter js_pg <pattern>` (adapters: `js_pg`, `js_neon`, etc.).
+  - For error assertions, use `result.name === 'PrismaClientKnownRequestError'` and `result.code` (not `instanceof`).
+  - Use `idForProvider(provider)` from `_utils/idForProvider` for portable ID field definitions.
+
 - **Docs & references**: `ARCHITECTURE.md` contains dependency graphs (requires GraphViz to regenerate), `docker/README.md` explains local DB setup, `examples/` provides sample apps, and `sandbox/` hosts debugging helpers like the DMMF explorer.

 - **Client architecture (Prisma 7)**:
@@ -48,6 +59,14 @@

 - **Environment loading**: Prisma 7 removes automatic `.env` loading.

+- **Driver adapter error handling**:
+  - Database errors are mapped in each adapter's `errors.ts` (e.g., `packages/adapter-pg/src/errors.ts`).
+  - `MappedError` type in `packages/driver-adapter-utils/src/types.ts` defines all known error kinds.
+  - `convertDriverError()` in each adapter maps database-specific error codes to `MappedError` kinds.
+  - `rethrowAsUserFacing()` in `packages/client-engine-runtime/src/user-facing-error.ts` maps `MappedError` kinds to Prisma error codes (P2xxx).
+  - To add a new error mapping: (1) add kind to `MappedError` in driver-adapter-utils, (2) map database error code in relevant adapter(s), (3) add Prisma code mapping in `getErrorCode()` and message in `renderErrorMessage()`.
+  - Raw queries (`$executeRaw`, `$queryRaw`) use `rethrowAsUserFacingRawError()` which always returns P2010; regular Prisma operations use `rethrowAsUserFacing()`.
+
 - **SQL Commenter packages**:
   - `@prisma/sqlcommenter`: Core types (`SqlCommenterPlugin`, `SqlCommenterContext`, `SqlCommenterQueryInfo`, `SqlCommenterTags`) for building sqlcommenter plugins.
   - `@prisma/sqlcommenter-query-tags`: AsyncLocalStorage-based plugin for adding ad-hoc tags via `withQueryTags()` and `withMergedQueryTags()`.
@@ -62,7 +81,7 @@
   - `packages/migrate/src/__tests__/__helpers__/context.ts` sets up Jest helpers including config contributors.
   - `packages/config` defines `PrismaConfigInternal`; inspect when validating config assumptions.
   - `@prisma/ts-builders` provides a fluent API for generating TypeScript code (interfaces, types, properties with doc comments).
-  - `@prisma/driver-adapter-utils` defines core interfaces: `SqlQuery`, `SqlQueryable`, `SqlDriverAdapter`, `SqlDriverAdapterFactory`.
+  - `@prisma/driver-adapter-utils` defines core interfaces: `SqlQuery`, `SqlQueryable`, `SqlDriverAdapter`, `SqlDriverAdapterFactory`, and `MappedError` for error handling.
   - `@prisma/client-engine-runtime` exports query interpreter, transaction manager, and related utilities.

 - **Coding conventions**:
diff --git a/packages/adapter-neon/src/errors.ts b/packages/adapter-neon/src/errors.ts
index 2fe00e83b59e..cb3009865b31 100644
--- a/packages/adapter-neon/src/errors.ts
+++ b/packages/adapter-neon/src/errors.ts
@@ -25,6 +25,11 @@ function mapDriverError(error: DatabaseError): MappedError {
         kind: 'ValueOutOfRange',
         cause: error.message,
       }
+    case '22P02':
+      return {
+        kind: 'InvalidInputValue',
+        message: error.message,
+      }
     case '23505': {
       const fields = error.detail
         ?.match(/Key \(([^)]+)\)/)
diff --git a/packages/adapter-pg/src/errors.ts b/packages/adapter-pg/src/errors.ts
index 18c586fee06f..e7188172231c 100644
--- a/packages/adapter-pg/src/errors.ts
+++ b/packages/adapter-pg/src/errors.ts
@@ -69,6 +69,11 @@ function mapDriverError(error: DatabaseError): MappedError {
         kind: 'ValueOutOfRange',
         cause: error.message,
       }
+    case '22P02':
+      return {
+        kind: 'InvalidInputValue',
+        message: error.message,
+      }
     case '23505': {
       const fields = error.detail
         ?.match(/Key \(([^)]+)\)/)
diff --git a/packages/adapter-ppg/src/errors.ts b/packages/adapter-ppg/src/errors.ts
index 84fa4c798163..c1a5622d39b4 100644
--- a/packages/adapter-ppg/src/errors.ts
+++ b/packages/adapter-ppg/src/errors.ts
@@ -25,6 +25,11 @@ function mapDriverError(error: DatabaseError): MappedError {
         kind: 'ValueOutOfRange',
         cause: error.message,
       }
+    case '22P02':
+      return {
+        kind: 'InvalidInputValue',
+        message: error.message,
+      }
     case '23505': {
       const fields = error.details.detail
         ?.match(/Key \(([^)]+)\)/)
diff --git a/packages/client-engine-runtime/src/user-facing-error.ts b/packages/client-engine-runtime/src/user-facing-error.ts
index 61b42e362348..682443e73fcd 100644
--- a/packages/client-engine-runtime/src/user-facing-error.ts
+++ b/packages/client-engine-runtime/src/user-facing-error.ts
@@ -79,6 +79,8 @@ function getErrorCode(err: DriverAdapterError): string | undefined {
       return 'P2002'
     case 'ForeignKeyConstraintViolation':
       return 'P2003'
+    case 'InvalidInputValue':
+      return 'P2007'
     case 'UnsupportedNativeDataType':
       return 'P2010'
     case 'NullConstraintViolation':
@@ -176,6 +178,8 @@ function renderErrorMessage(err: DriverAdapterError): string | undefined {
       return `Error in external connector (id ${err.cause.id})`
     case 'TooManyConnections':
       return `Too many database connections opened: ${err.cause.cause}`
+    case 'InvalidInputValue':
+      return `Invalid input value: ${err.cause.message}`
     case 'sqlite':
     case 'postgres':
     case 'mysql':
diff --git a/packages/driver-adapter-utils/src/types.ts b/packages/driver-adapter-utils/src/types.ts
index cd9354592f33..6523e04933aa 100644
--- a/packages/driver-adapter-utils/src/types.ts
+++ b/packages/driver-adapter-utils/src/types.ts
@@ -141,6 +141,10 @@ export type MappedError =
       kind: 'ValueOutOfRange'
       cause: string
     }
+  | {
+      kind: 'InvalidInputValue'
+      message: string
+    }
   | {
       kind: 'MissingFullTextSearchIndex'
     }

PATCH

echo "Patch applied successfully."
