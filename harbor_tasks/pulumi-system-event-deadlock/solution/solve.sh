#!/usr/bin/env bash
# Gold-patch oracle for pulumi/pulumi#22433.
# Applies the upstream fix to pkg/backend/display/progress.go.
set -euo pipefail

cd /workspace/pulumi

# Idempotency: if the distinctive comment from the fix is already present,
# skip re-applying. The agent's solution may have used a different style,
# so we only re-apply when the file still carries the buggy `defer` pattern.
if grep -q "Release the lock before calling the renderer" pkg/backend/display/progress.go; then
    echo "Gold patch already applied — skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/changelog/pending/20260401--cli-display--fix-deadlock-in-message-renderer-when-cancelling-an-operation.yaml b/changelog/pending/20260401--cli-display--fix-deadlock-in-message-renderer-when-cancelling-an-operation.yaml
new file mode 100644
index 000000000000..1a92c5405189
--- /dev/null
+++ b/changelog/pending/20260401--cli-display--fix-deadlock-in-message-renderer-when-cancelling-an-operation.yaml
@@ -0,0 +1,4 @@
+changes:
+- type: fix
+  scope: cli/display
+  description: Fix deadlock in message renderer when cancelling an operation
diff --git a/pkg/backend/display/progress.go b/pkg/backend/display/progress.go
index 944fc890ff3b..142cdd57795b 100644
--- a/pkg/backend/display/progress.go
+++ b/pkg/backend/display/progress.go
@@ -1385,13 +1385,16 @@ func (display *ProgressDisplay) handleSystemEvent(payload engine.StdoutEventPayl
 	// We need to take the writer lock here because ensureHeaderAndStackRows expects to be
 	// called under the write lock.
 	display.eventMutex.Lock()
-	defer display.eventMutex.Unlock()

 	// Make sure we have a header to display
 	display.ensureHeaderAndStackRows()

 	display.systemEventPayloads = append(display.systemEventPayloads, payload)

+	// Release the lock before calling the renderer, because it may call back into a method (like generateTreeNodes)
+	// that acquires eventMutex.RLock(), causing a deadlock.
+	display.eventMutex.Unlock()
+
 	display.renderer.systemMessage(payload)
 }

PATCH

echo "Gold patch applied."
