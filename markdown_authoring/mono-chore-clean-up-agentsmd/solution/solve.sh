#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mono

# Idempotency guard
if grep -qF "- Re-exports are common: main packages re-export from sub-packages (e.g., `packa" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,16 +1,28 @@
-# Rocicorp Monorepo - Copilot Instructions
+# Rocicorp Monorepo Instructions
 
 ## Architecture Overview
 
 This monorepo contains **Zero** (real-time sync platform) and **Replicache** (client-side data layer), built as complementary technologies for building reactive, sync-enabled applications.
 
-### Key Components
+### Repo Structure
 
-- **packages/zero-client**: Main Zero client library using Replicache under the hood
-- **packages/zero-cache**: Server-side cache and sync engine
-- **packages/zql**: IVM (Incremental View Maintenance) query engine and language
-- **packages/replicache**: Core client-side data synchronization library
-- **apps/zbugs**: Reference application demonstrating Zero/Replicache patterns
+```
+mono/
+├── packages/          # 29 core packages (libraries and engines)
+│   ├── zero-client    # Main Zero client (uses Replicache)
+│   ├── zero-cache     # Server-side cache and sync engine
+│   ├── zero-server    # Server-side mutations/queries
+│   ├── zero-schema    # Schema definition builder
+│   ├── zql            # IVM (Incremental View Maintenance) query engine and language
+│   ├── replicache     # Core client-side sync library
+│   └── shared         # Shared utilities and testing helpers
+├── apps/              # 3 applications
+│   ├── zbugs          # Reference app (React + Wouter + Zero + PostgreSQL)
+│   ├── otel-proxy     # OpenTelemetry proxy
+│   └── zql-viz        # Query visualization tool
+├── tools/             # 5 development tools
+└── prod/              # Production deployment (SST/Pulumi)
+```
 
 ### Data Flow Architecture
 
@@ -34,11 +46,20 @@ npm run lint              # oxlint with type-awareness
 npm run format            # Prettier formatting
 ```
 
-**Always run `lint`, `format` and `check-types` after every change**
+**Always run `lint`, `format` and `check-types` after every change.**
 
 ### Package-Level Commands
 
-Each package supports: `test`, `check-types`, `lint`, `format`, `build`
+Prefer package-level commands when possible. Each package supports: `test`, `check-types`, `lint`, `format`, `build`. e.g.:
+
+```bash
+npm --workspace=zero-client run format
+npm --workspace=zero-cache run lint
+npm --workspace=zero-server run check-types
+
+# Run specific test file
+npm --workspace=zero-client run test -- zero.test
+```
 
 ### Zero Cache Development
 
@@ -85,33 +106,59 @@ const user = table('user')
 ### Testing Patterns
 
 - Use **vitest** for all testing
-- Tests are co-located with source files (`.test.ts`)
+- Tests are co-located with source files using environment-specific naming:
+  - `.test.ts` - Standard tests (Node.js environment)
+  - `.node.test.ts` - Node-specific tests (Replicache)
+  - `.web.test.ts` - Browser tests (Replicache)
+  - `.pg.test.ts` - PostgreSQL integration tests
 - Multiple vitest configs for different environments (e.g., `vitest.config.pg-16.ts` for PostgreSQL tests)
 - Test files automatically discovered by the root vitest config
 - Prefer `test` over `it` for consistency
 
 ### Import Patterns
 
-- Packages import from each other using workspace names (`zero-client`, `shared`, etc.)
-- Cross-package dependencies are managed through the monorepo structure
-- Re-exports are common (see `packages/zero/src/zero.ts` → `packages/zero-client/src/mod.ts`)
-- Do not import from `mod.ts`. Use relative paths.
+- **DO NOT import from `mod.ts`**: Use direct relative paths instead
+
+  ```typescript
+  // Correct - use relative path
+  import {helper} from './helper.ts';
+
+  // Incorrect - don't import from mod.ts
+  import {helper} from './mod.ts';
+  ```
+
+- Re-exports are common: main packages re-export from sub-packages (e.g., `packages/zero/src/mod.ts` → exports from `zero-client`, `zero-server`)
 
-## Database Integration
+## Database
 
 ### Zero + PostgreSQL
 
-Zero maintains a dual-database setup:
+Zero is a streaming database:
 
-- **PostgreSQL**: Source of truth for server data
-- **SQLite**: Client-side replica managed by Replicache
+- **PostgreSQL**: Source of truth for data
+- **SQLite**: Server-side replica managed by `zero-cache`
+- **Replicache**: Client-side store managed by `zero-client` and `replicache`, in IndexedDB by default
 
 ### Schema Migrations
 
 - Use Drizzle for PostgreSQL schema management (`db-migrate`, `db-seed`)
 - Zero schema definitions are separate from PostgreSQL schema
 - Apps like zbugs demonstrate the connection between PostgreSQL tables and Zero schemas
 
+## Git Conventions
+
+### Commit Messages
+
+Follow conventional commits format:
+
+```
+type(scope): description
+```
+
+- `feat(zero-client): add support for custom mutations`
+- `fix(zero-cache): resolve memory leak in connection pool`
+- `chore(deps): update vitest to 3.2.4`
+
 ## Debugging and Development
 
 ### Zero Cache Debugging
PATCH

echo "Gold patch applied."
