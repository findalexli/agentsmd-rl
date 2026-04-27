#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-dev-kit

# Idempotency guard
if grep -qF "description: \"Manage Databricks workspace connections: check current workspace, " "databricks-skills/databricks-config/SKILL.md" && grep -qF "description: \"Databricks documentation reference via llms.txt index. Use when ot" "databricks-skills/databricks-docs/SKILL.md" && grep -qF "description: \"Patterns and best practices for Lakebase Autoscaling (next-gen man" "databricks-skills/databricks-lakebase-autoscale/SKILL.md" && grep -qF "description: \"Patterns and best practices for Lakebase Provisioned (Databricks m" "databricks-skills/databricks-lakebase-provisioned/SKILL.md" && grep -qF "description: \"Comprehensive guide to Spark Structured Streaming for production w" "databricks-skills/databricks-spark-structured-streaming/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/databricks-skills/databricks-config/SKILL.md b/databricks-skills/databricks-config/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: databricks-config
-description: "Manage Databricks workspace connections: check which workspace you're connected to, switch workspaces, list available workspaces, or authenticate to a new workspace."
+description: "Manage Databricks workspace connections: check current workspace, switch profiles, list available workspaces, or authenticate to a new workspace. Use when the user mentions \"switch workspace\", \"which workspace\", \"current profile\", \"databrickscfg\", \"connect to workspace\", or \"databricks auth\"."
 ---
 
 Use the `manage_workspace` MCP tool for all workspace operations. Do NOT edit `~/.databrickscfg`, use Bash, or use the Databricks CLI.
diff --git a/databricks-skills/databricks-docs/SKILL.md b/databricks-skills/databricks-docs/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: databricks-docs
-description: "Databricks documentation reference. Use as a lookup resource alongside other skills and MCP tools for comprehensive guidance."
+description: "Databricks documentation reference via llms.txt index. Use when other skills do not cover a topic, looking up unfamiliar Databricks features, or needing authoritative docs on APIs, configurations, or platform capabilities."
 ---
 
 # Databricks Documentation Reference
diff --git a/databricks-skills/databricks-lakebase-autoscale/SKILL.md b/databricks-skills/databricks-lakebase-autoscale/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: databricks-lakebase-autoscale
-description: "Patterns and best practices for using Lakebase Autoscaling (next-gen managed PostgreSQL) with autoscaling, branching, scale-to-zero, and instant restore."
+description: "Patterns and best practices for Lakebase Autoscaling (next-gen managed PostgreSQL). Use when creating or managing Lakebase Autoscaling projects, configuring autoscaling compute or scale-to-zero, working with database branching for dev/test workflows, implementing reverse ETL via synced tables, or connecting applications to Lakebase with OAuth credentials."
 ---
 
 # Lakebase Autoscaling
diff --git a/databricks-skills/databricks-lakebase-provisioned/SKILL.md b/databricks-skills/databricks-lakebase-provisioned/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: databricks-lakebase-provisioned
-description: "Patterns and best practices for using Lakebase Provisioned (Databricks managed PostgreSQL) for OLTP workloads."
+description: "Patterns and best practices for Lakebase Provisioned (Databricks managed PostgreSQL) for OLTP workloads. Use when creating Lakebase instances, connecting applications or Databricks Apps to PostgreSQL, implementing reverse ETL via synced tables, storing agent or chat memory, or configuring OAuth authentication for Lakebase."
 ---
 
 # Lakebase Provisioned
diff --git a/databricks-skills/databricks-spark-structured-streaming/SKILL.md b/databricks-skills/databricks-spark-structured-streaming/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: databricks-spark-structured-streaming
-description: Comprehensive guide to Spark Structured Streaming for production workloads. Use when building streaming pipelines, implementing real-time data processing, handling stateful operations, or optimizing streaming performance.
+description: "Comprehensive guide to Spark Structured Streaming for production workloads. Use when building streaming pipelines, working with Kafka ingestion, implementing Real-Time Mode (RTM), configuring triggers (processingTime, availableNow), handling stateful operations with watermarks, optimizing checkpoints, performing stream-stream or stream-static joins, writing to multiple sinks, or tuning streaming cost and performance."
 ---
 
 # Spark Structured Streaming
PATCH

echo "Gold patch applied."
