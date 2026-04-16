#!/bin/bash
set -e

cd /workspace/prometheus

# Check if already applied (idempotency check)
if grep -q "func (t \*testRunner) atomicWrite" discovery/file/file_test.go; then
    echo "Fix already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/discovery/file/file_test.go b/discovery/file/file_test.go
index b79f73eb752..80239875ce1 100644
--- a/discovery/file/file_test.go
+++ b/discovery/file/file_test.go
@@ -69,25 +69,55 @@ func (t *testRunner) copyFile(src string) string {
 	return t.copyFileTo(src, filepath.Base(src))
 }

-// copyFileTo copies a file with a different name to the runner's directory.
+// copyFileTo atomically copies a file with a different name to the runner's directory.
 func (t *testRunner) copyFileTo(src, name string) string {
 	t.Helper()

-	newf, err := os.ReadFile(src)
+	content, err := os.ReadFile(src)
 	require.NoError(t, err)

 	dst := filepath.Join(t.dir, name)
-	// Use os.WriteFile to avoid an os.Rename race condition on Windows.
-	require.NoError(t, os.WriteFile(dst, newf, 0o644))
+	t.atomicWrite(dst, content)

 	return dst
 }

-// writeString writes a string to a file.
+// writeString atomically writes a string to a file.
 func (t *testRunner) writeString(file, data string) {
 	t.Helper()
-	// Use os.WriteFile to avoid an os.Rename race condition on Windows.
-	require.NoError(t, os.WriteFile(file, []byte(data), 0o644))
+	t.atomicWrite(file, []byte(data))
+}
+
+// atomicWrite writes data to dst atomically by writing to a temporary file
+// and renaming it. The temp file is created outside the watched directory to
+// avoid triggering spurious fsnotify events that could cause readFile to hold
+// an open handle on dst (which would make os.Rename fail on Windows).
+func (t *testRunner) atomicWrite(dst string, data []byte) {
+	t.Helper()
+
+	// Create the temp file via t.TempDir() rather than in t.dir (the watched
+	// directory). t.TempDir() returns a fresh directory on the same filesystem
+	// as t.dir, so os.Rename works, and cleanup is handled by the test framework.
+	tmp, err := os.CreateTemp(t.TempDir(), ".sd-test-*")
+	require.NoError(t, err)
+
+	_, err = tmp.Write(data)
+	require.NoError(t, err)
+	require.NoError(t, tmp.Close())
+
+	// On Windows, os.Rename fails if another process holds an open handle
+	// on dst. This can happen if a previous refresh cycle's readFile call
+	// hasn't released the file yet. Retry a few times to handle this;
+	// on Linux/macOS os.Rename always succeeds regardless, so the retry
+	// never triggers.
+	for retries := 0; ; retries++ {
+		err = os.Rename(tmp.Name(), dst)
+		if err == nil || retries >= 5 {
+			break
+		}
+		time.Sleep(50 * time.Millisecond)
+	}
+	require.NoError(t, err)
 }

 // appendString appends a string to a file.
PATCH

echo "Fix applied successfully"
