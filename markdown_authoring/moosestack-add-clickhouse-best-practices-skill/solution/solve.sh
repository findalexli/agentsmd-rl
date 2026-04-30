#!/usr/bin/env bash
set -euo pipefail

cd /workspace/moosestack

# Idempotency guard
if grep -qF "Each rule includes MooseStack TypeScript/Python examples. When reviewing or impl" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -100,4 +100,15 @@ rm -rf node_modules && pnpm install
 
 ## Key Technologies
 
-Rust (CLI), TypeScript (libs/web), Python (lib), ClickHouse (OLAP), Redpanda/Kafka (streaming), Temporal (workflows), Redis (state)
\ No newline at end of file
+Rust (CLI), TypeScript (libs/web), Python (lib), ClickHouse (OLAP), Redpanda/Kafka (streaming), Temporal (workflows), Redis (state)
+
+## ClickHouse Best Practices
+
+When working with MooseStack data models, ClickHouse schemas, queries, or configurations, reference the `moosestack-clickhouse-best-practices` skill. It contains rules covering:
+- Schema design (primary keys, data types, partitioning)
+- Query optimization (JOINs, materialized views, indices)
+- Insert strategy (batching, async inserts, avoiding mutations)
+
+Each rule includes MooseStack TypeScript/Python examples. When reviewing or implementing ClickHouse-related code, read relevant rule files and cite specific rules in your guidance.
+
+To install the skill: `npx skills add 514-labs/agent-skills`
PATCH

echo "Gold patch applied."
