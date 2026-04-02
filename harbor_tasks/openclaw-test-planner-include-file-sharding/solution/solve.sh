#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency: check if fix already applied
if grep -q 'countUnitEntryFilters' scripts/test-planner/planner.mjs 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/scripts/test-planner/executor.mjs b/scripts/test-planner/executor.mjs
index 5956d755f6f3..343547feea5f 100644
--- a/scripts/test-planner/executor.mjs
+++ b/scripts/test-planner/executor.mjs
@@ -15,6 +15,17 @@ import {
 } from "../test-parallel-utils.mjs";
 import { countExplicitEntryFilters, getExplicitEntryFilters } from "./vitest-args.mjs";

+const countUnitEntryFilters = (unit) => {
+  const explicitFilterCount = countExplicitEntryFilters(unit.args);
+  if (explicitFilterCount !== null) {
+    return explicitFilterCount;
+  }
+  if (Array.isArray(unit.includeFiles) && unit.includeFiles.length > 0) {
+    return unit.includeFiles.length;
+  }
+  return null;
+};
+
 export function resolvePnpmCommandInvocation(options = {}) {
   const npmExecPath = typeof options.npmExecPath === "string" ? options.npmExecPath.trim() : "";
   if (npmExecPath && path.isAbsolute(npmExecPath)) {
@@ -253,7 +264,7 @@ export function formatPlanOutput(plan) {
     `runtime=${plan.runtimeCapabilities.runtimeProfileName} mode=${plan.runtimeCapabilities.mode} intent=${plan.runtimeCapabilities.intentProfile} memoryBand=${plan.runtimeCapabilities.memoryBand} loadBand=${plan.runtimeCapabilities.loadBand} failurePolicy=${plan.failurePolicy} vitestMaxWorkers=${String(plan.executionBudget.vitestMaxWorkers ?? "default")} topLevelParallel=${plan.topLevelParallelEnabled ? String(plan.topLevelParallelLimit) : "off"}`,
     ...plan.selectedUnits.map(
       (unit) =>
-        `${unit.id} filters=${String(countExplicitEntryFilters(unit.args) ?? "all")} maxWorkers=${String(
+        `${unit.id} filters=${String(countUnitEntryFilters(unit) ?? "all")} maxWorkers=${String(
           unit.maxWorkers ?? "default",
         )} surface=${unit.surface} isolate=${unit.isolate ? "yes" : "no"} pool=${unit.pool}`,
     ),
@@ -810,7 +821,7 @@ export async function executePlan(plan, options = {}) {
       results.push(await runOnce(unit, extraArgs));
       return results;
     }
-    const explicitFilterCount = countExplicitEntryFilters(unit.args);
+    const explicitFilterCount = countUnitEntryFilters(unit);
     const topLevelAssignedShard = plan.topLevelSingleShardAssignments.get(unit);
     if (topLevelAssignedShard !== undefined) {
       if (plan.shardIndexOverride !== null && plan.shardIndexOverride !== topLevelAssignedShard) {
diff --git a/scripts/test-planner/planner.mjs b/scripts/test-planner/planner.mjs
index bf8eb2dab5dd..2c694068e71a 100644
--- a/scripts/test-planner/planner.mjs
+++ b/scripts/test-planner/planner.mjs
@@ -19,6 +19,17 @@ import {
   SINGLE_RUN_ONLY_FLAGS,
 } from "./vitest-args.mjs";

+const countUnitEntryFilters = (unit) => {
+  const explicitFilterCount = countExplicitEntryFilters(unit.args);
+  if (explicitFilterCount !== null) {
+    return explicitFilterCount;
+  }
+  if (Array.isArray(unit.includeFiles) && unit.includeFiles.length > 0) {
+    return unit.includeFiles.length;
+  }
+  return null;
+};
+
 const parseEnvNumber = (env, name, fallback) => {
   const parsed = Number.parseInt(env[name] ?? "", 10);
   return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
@@ -1116,7 +1127,7 @@ const buildTopLevelSingleShardAssignments = (context, units) => {
     if (unit.fixedShardIndex !== undefined) {
       return false;
     }
-    const explicitFilterCount = countExplicitEntryFilters(unit.args);
+    const explicitFilterCount = countUnitEntryFilters(unit);
     if (explicitFilterCount === null) {
       return false;
     }
@@ -1364,7 +1375,7 @@ export function buildCIExecutionManifest(scopeInput = {}, options = {}) {
 }

 export const formatExecutionUnitSummary = (unit) =>
-  `${unit.id} filters=${String(countExplicitEntryFilters(unit.args) || "all")} maxWorkers=${String(
+  `${unit.id} filters=${String(countUnitEntryFilters(unit) || "all")} maxWorkers=${String(
     unit.maxWorkers ?? "default",
   )} surface=${unit.surface} isolate=${unit.isolate ? "yes" : "no"} pool=${unit.pool}`;

PATCH

echo "Patch applied successfully."
