#!/bin/bash
set -e

cd /workspace/containerd

# Apply the fix for klog stderrthreshold behavior
# This patch ensures stderrthreshold is honored when logtostderr is enabled
patch -p1 <<'PATCH'
diff --git a/plugins/cri/runtime/plugin.go b/plugins/cri/runtime/plugin.go
index b4ee60f838d41..d3f748584d7b7a 100644
--- a/plugins/cri/runtime/plugin.go
+++ b/plugins/cri/runtime/plugin.go
@@ -178,6 +178,13 @@ func setGLogLevel() error {
 	l := log.GetLevel()
 	fs := flag.NewFlagSet("klog", flag.PanicOnError)
 	klog.InitFlags(fs)
+	// Opt into fixed stderrthreshold behavior (kubernetes/klog#212).
+	if err := fs.Set("legacy_stderr_threshold_behavior", "false"); err != nil {
+		return err
+	}
+	if err := fs.Set("stderrthreshold", "INFO"); err != nil {
+		return err
+	}
 	if err := fs.Set("logtostderr", "true"); err != nil {
 		return err
 	}
PATCH

# Verify the patch was applied (idempotency check)
if ! grep -q "legacy_stderr_threshold_behavior" plugins/cri/runtime/plugin.go; then
    echo "ERROR: Patch was not applied successfully"
    exit 1
fi

echo "Patch applied successfully"
