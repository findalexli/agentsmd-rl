#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency: check if already fixed (the re-export line is the fix)
if grep -q 'export.*formatDurationCompact.*from.*infra/format-time' src/shared/subagents-format.ts; then
  echo "Fix already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/agents/subagent-control.ts b/src/agents/subagent-control.ts
index 9127d88f113c..fcc73f59ca1f 100644
--- a/src/agents/subagent-control.ts
+++ b/src/agents/subagent-control.ts
@@ -345,7 +345,7 @@ export function buildSubagentList(params: {
           }),
       ),
     );
-    const runtime = formatDurationCompact(runtimeMs);
+    const runtime = formatDurationCompact(runtimeMs) ?? "n/a";
     const label = truncateLine(resolveSubagentLabel(entry), 48);
     const task = truncateLine(entry.task.trim(), params.taskMaxChars ?? 72);
     const line = `${index}. ${label} (${resolveModelDisplay(sessionEntry, entry.model)}, ${runtime}${usageText ? `, ${usageText}` : ""}) ${status}${task.toLowerCase() !== label.toLowerCase() ? ` - ${task}` : ""}`;
diff --git a/src/auto-reply/reply/commands-subagents/shared.ts b/src/auto-reply/reply/commands-subagents/shared.ts
index 3d2b9726da38..7da9ca3a69d9 100644
--- a/src/auto-reply/reply/commands-subagents/shared.ts
+++ b/src/auto-reply/reply/commands-subagents/shared.ts
@@ -148,7 +148,7 @@ export function formatSubagentListLine(params: {
   const usageText = formatTokenUsageDisplay(params.sessionEntry);
   const label = truncateLine(formatRunLabel(params.entry, { maxLength: 48 }), 48);
   const task = formatTaskPreview(params.entry.task);
-  const runtime = formatDurationCompact(params.runtimeMs);
+  const runtime = formatDurationCompact(params.runtimeMs) ?? "n/a";
   const status = resolveDisplayStatus(params.entry, {
     pendingDescendants: params.pendingDescendants,
   });
diff --git a/src/shared/subagents-format.ts b/src/shared/subagents-format.ts
index 643c4b58ca58..c24042a0a0dd 100644
--- a/src/shared/subagents-format.ts
+++ b/src/shared/subagents-format.ts
@@ -1,20 +1,4 @@
-export function formatDurationCompact(valueMs?: number) {
-  if (!valueMs || !Number.isFinite(valueMs) || valueMs <= 0) {
-    return "n/a";
-  }
-  const minutes = Math.max(1, Math.round(valueMs / 60_000));
-  if (minutes < 60) {
-    return `${minutes}m`;
-  }
-  const hours = Math.floor(minutes / 60);
-  const minutesRemainder = minutes % 60;
-  if (hours < 24) {
-    return minutesRemainder > 0 ? `${hours}h${minutesRemainder}m` : `${hours}h`;
-  }
-  const days = Math.floor(hours / 24);
-  const hoursRemainder = hours % 24;
-  return hoursRemainder > 0 ? `${days}d${hoursRemainder}h` : `${days}d`;
-}
+export { formatDurationCompact } from "../infra/format-time/format-duration.ts";

 export function formatTokenShort(value?: number) {
   if (!value || !Number.isFinite(value) || value <= 0) {

PATCH

echo "Fix applied: replaced buggy duplicate formatDurationCompact with re-export of canonical implementation."
