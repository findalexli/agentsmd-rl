#!/usr/bin/env bash
set -euo pipefail

cd /workspace/langfuse

# Idempotency guard
if grep -qF "The most important domain objects are in [observations.ts](mdc:packages/shared/s" ".cursor/rules/global.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/global.mdc b/.cursor/rules/global.mdc
@@ -1,20 +1,28 @@
 ---
-description: 
-globs: 
+description:
+globs:
 alwaysApply: true
 ---
+
 ## Project setup
+
 - This project is a Turborepo monorepo
 - We build two containers, web (./web) and worker (./worker)
 - We have shared code between these two in the shared package (./packages/shared). For that package, we have different entry points [package.json](mdc:packages/shared/package.json).
 
-
 ## Domain layer
-The most important domain objects are in [observations.ts](mdc:packages/shared/src/domain/observations.ts), [traces.ts](mdc:packages/shared/src/domain/traces.ts), [scores.ts](mdc:packages/shared/src/domain/scores.ts).
 
+The most important domain objects are in [observations.ts](mdc:packages/shared/src/domain/observations.ts), [traces.ts](mdc:packages/shared/src/domain/traces.ts), [scores.ts](mdc:packages/shared/src/domain/scores.ts).
 
 ## Database schema
+
 We use Postgres and Clickhouse.
+
 - The postgres schema is in [schema.prisma](mdc:packages/shared/prisma/schema.prisma)
 - The clickhouse schema is in [0001_traces.up.sql](mdc:packages/shared/clickhouse/migrations/clustered/0001_traces.up.sql), [0002_observations.up.sql](mdc:packages/shared/clickhouse/migrations/clustered/0002_observations.up.sql), [0003_scores.up.sql](mdc:packages/shared/clickhouse/migrations/clustered/0003_scores.up.sql)
 
+## Cursor Background/Cloud Agent
+
+When running in a background/cloud agent, please adhere to the following rules:
+
+- Before finishing a task, please run prettier via `pnpm format` to format the code of the repository. Otherwise, the CI check will fail on the change.
PATCH

echo "Gold patch applied."
