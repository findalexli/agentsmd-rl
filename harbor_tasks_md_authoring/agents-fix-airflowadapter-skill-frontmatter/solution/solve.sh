#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents

# Idempotency guard
if grep -qF "description: Airflow adapter pattern for v2/v3 API compatibility. Use when worki" "astro-airflow-mcp/.claude/skills/airflow-adapter/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/astro-airflow-mcp/.claude/skills/airflow-adapter/SKILL.md b/astro-airflow-mcp/.claude/skills/airflow-adapter/SKILL.md
@@ -1,8 +1,6 @@
 ---
-description: Airflow adapter pattern for v2/v3 API compatibility
-globs:
-  - src/astro_airflow_mcp/adapters/**
-  - src/astro_airflow_mcp/server.py
+name: airflow-adapter
+description: Airflow adapter pattern for v2/v3 API compatibility. Use when working with adapters, version detection, or adding new API methods that need to work across Airflow 2.x and 3.x.
 ---
 
 # Airflow Adapter Pattern
PATCH

echo "Gold patch applied."
