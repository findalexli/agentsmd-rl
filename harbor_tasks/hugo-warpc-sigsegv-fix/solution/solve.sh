#!/bin/bash
set -e

cd /workspace/hugo

# Check if already applied (idempotency)
if grep -q "if d.startErr == nil" internal/warpc/warpc.go; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply gold patch
patch -p1 <<'PATCH'
diff --git a/internal/warpc/warpc.go b/internal/warpc/warpc.go
index e62e6b09ea7..58dcf5dc7d8 100644
--- a/internal/warpc/warpc.go
+++ b/internal/warpc/warpc.go
@@ -776,8 +776,10 @@ func (d *lazyDispatcher[Q, R]) start() (Dispatcher[Q, R], error) {
 	d.startOnce.Do(func() {
 		start := time.Now()
 		d.dispatcher, d.startErr = Start[Q, R](d.opts)
-		d.started = true
-		d.opts.Infof("started dispatcher in %s", time.Since(start))
+		if d.startErr == nil {
+			d.started = true
+			d.opts.Infof("started dispatcher in %s", time.Since(start))
+		}
 	})
 	return d.dispatcher, d.startErr
 }
PATCH

echo "Patch applied successfully"
