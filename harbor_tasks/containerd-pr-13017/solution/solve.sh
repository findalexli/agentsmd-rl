#!/bin/bash
set -e

cd /workspace/containerd

# Apply the fix for PR #13017 - avoid content storage pollution by limiting /blobs fallback
patch -p1 <<'PATCH'
diff --git a/core/remotes/docker/resolver.go b/core/remotes/docker/resolver.go
index 74a5bd08c9500..470a3ea6e350b 100644
--- a/core/remotes/docker/resolver.go
+++ b/core/remotes/docker/resolver.go
@@ -292,6 +292,14 @@ func (r *dockerResolver) Resolve(ctx context.Context, ref string) (string, ocisp
 	}

 	for _, u := range paths {
+		// falling back to /blobs endpoint should happen in extreme cases - those to
+		// support legacy registries. we want to limit the fallback to when /manifests endpoint
+		// returned 404. Falling back on transient errors could do more harm, like polluting
+		// the local content store with incorrectly typed descriptors as /blobs endpoint tends
+		// always return with application/octet-stream.
+		if firstErrPriority > 2 {
+			break
+		}
 		for i, host := range hosts {
 			ctx := log.WithLogger(ctx, log.G(ctx).WithField("host", host.Host))

PATCH

echo "Patch applied successfully"
