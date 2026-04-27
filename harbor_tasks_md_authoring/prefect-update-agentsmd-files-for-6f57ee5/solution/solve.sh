#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "The events page displays at most 50 events in descending chronological order. In" "ui-v2/e2e/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/e2e/AGENTS.md b/ui-v2/e2e/AGENTS.md
@@ -227,6 +227,25 @@ await emitEvents(apiClient, [
 
 The `buildTestEvent()` helper in `e2e/fixtures/api-helpers/events.ts` accepts an optional `occurred` parameter (defaults to `new Date().toISOString()`). Tests that don't backdate will be flaky — passing when the minute boundary doesn't fall mid-test, failing when it does.
 
+### Events Page Pagination Pitfall
+
+The events page displays at most 50 events in descending chronological order. In busy CI environments, parallel shards generate background events (deployment runs, work-pool polls, etc.) that can push test-specific events off the first page, causing assertions to fail even though the events were emitted correctly.
+
+Scope events-page tests to specific resources using the `resource` query parameter:
+
+```typescript
+const resourceFilter = encodeURIComponent(
+  JSON.stringify([
+    flowRunResourceId,
+    "prefect.deployment.",
+    "prefect.work-pool.",
+  ]),
+);
+await page.goto(`/events?resource=${resourceFilter}`);
+```
+
+Pass the resource IDs (or prefixes) of the resources your test cares about. This keeps the result set small regardless of how much background activity other shards produce.
+
 ### Explicit Waits
 
 Avoid `waitForTimeout()` unless absolutely necessary. When required, always add a comment explaining why:
PATCH

echo "Gold patch applied."
