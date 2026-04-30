#!/usr/bin/env bash
# Gold solution: fix Tar.Sync() to return non-ErrNotExist stat errors
# instead of silently treating them as copyable paths.
set -euo pipefail

cd /workspace/compose

# Idempotency guard: if the distinctive line from the patch is already present,
# the fix has already been applied — exit cleanly.
if grep -q 'return fmt.Errorf("stat %q: %w", p.HostPath, err)' internal/sync/tar.go; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/internal/sync/tar.go b/internal/sync/tar.go
--- a/internal/sync/tar.go
+++ b/internal/sync/tar.go
@@ -73,10 +73,12 @@ func (t *Tar) Sync(ctx context.Context, service string, paths []*PathMapping) er
 	var pathsToCopy []PathMapping
 	var pathsToDelete []string
 	for _, p := range paths {
-		if _, err := os.Stat(p.HostPath); err != nil && errors.Is(err, fs.ErrNotExist) {
+		if _, err := os.Stat(p.HostPath); err == nil {
+			pathsToCopy = append(pathsToCopy, *p)
+		} else if errors.Is(err, fs.ErrNotExist) {
 			pathsToDelete = append(pathsToDelete, p.ContainerPath)
 		} else {
-			pathsToCopy = append(pathsToCopy, *p)
+			return fmt.Errorf("stat %q: %w", p.HostPath, err)
 		}
 	}

PATCH

echo "Applied tar.go fix."
