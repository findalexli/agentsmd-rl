#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents

# Idempotency guard
if grep -qF "shared-skills/airflow-2-to-3-migration/SKILL.md" "shared-skills/airflow-2-to-3-migration/SKILL.md" && grep -qF "name: check-freshness" "shared-skills/check-freshness/SKILL.md" && grep -qF "name: debug-dag" "shared-skills/debug-dag/SKILL.md" && grep -qF "name: discover-data" "shared-skills/discover-data/SKILL.md" && grep -qF "name: downstream-lineage" "shared-skills/downstream-lineage/SKILL.md" && grep -qF "name: profile-table" "shared-skills/profile-table/SKILL.md" && grep -qF "name: upstream-lineage" "shared-skills/upstream-lineage/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/shared-skills/airflow-2-to-3-migration/SKILL.md b/shared-skills/airflow-2-to-3-migration/SKILL.md

diff --git a/shared-skills/check-freshness/SKILL.md b/shared-skills/check-freshness/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: freshness
+name: check-freshness
 description: Quick data freshness check. Use when the user asks if data is up to date, when a table was last updated, if data is stale, or needs to verify data currency before using it.
 ---
 
diff --git a/shared-skills/debug-dag/SKILL.md b/shared-skills/debug-dag/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: diagnose
+name: debug-dag
 description: Debug a failed Airflow DAG run. Use when the user mentions DAG failures, task errors, broken pipelines, or asks why a DAG/task failed. Provides root cause analysis and remediation steps.
 ---
 
diff --git a/shared-skills/discover-data/SKILL.md b/shared-skills/discover-data/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: explore
+name: discover-data
 description: Discover and explore data for a concept or domain. Use when the user asks what data exists for a topic (e.g., "ARR", "customers", "orders"), wants to find relevant tables, or needs to understand what data is available before analysis.
 ---
 
diff --git a/shared-skills/downstream-lineage/SKILL.md b/shared-skills/downstream-lineage/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: impacts
+name: downstream-lineage
 description: Trace downstream data lineage and impact analysis. Use when the user asks what depends on this data, what breaks if something changes, downstream dependencies, or needs to assess change risk before modifying a table or DAG.
 ---
 
diff --git a/shared-skills/profile-table/SKILL.md b/shared-skills/profile-table/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: profile
+name: profile-table
 description: Deep-dive data profiling for a specific table. Use when the user asks to profile a table, wants statistics about a dataset, asks about data quality, or needs to understand a table's structure and content. Requires a table name.
 ---
 
diff --git a/shared-skills/upstream-lineage/SKILL.md b/shared-skills/upstream-lineage/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: sources
+name: upstream-lineage
 description: Trace upstream data lineage. Use when the user asks where data comes from, what feeds a table, upstream dependencies, data sources, or needs to understand data origins.
 ---
 
PATCH

echo "Gold patch applied."
