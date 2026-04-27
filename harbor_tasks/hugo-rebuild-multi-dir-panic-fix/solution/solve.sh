#!/bin/bash
set -euo pipefail

cd /workspace/hugo

if grep -q '^			keep := true$' hugolib/site.go; then
    echo "Gold patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/hugolib/site.go b/hugolib/site.go
index 07fe41d2a0f..3ceccc440ae 100644
--- a/hugolib/site.go
+++ b/hugolib/site.go
@@ -1316,15 +1316,18 @@ func (h *HugoSites) fileEventsContentPaths(p []pathChange) []pathChange {
 	// Remove all files below dir.
 	if len(dirs) > 0 {
 		n := 0
-		for _, d := range dirs {
-			dir := d.p.Path() + "/"
-			for _, o := range others {
-				if !strings.HasPrefix(o.p.Path(), dir) {
-					others[n] = o
-					n++
+		for _, o := range others {
+			keep := true
+			for _, d := range dirs {
+				if strings.HasPrefix(o.p.Path(), d.p.Path()+"/") {
+					keep = false
+					break
 				}
 			}
-
+			if keep {
+				others[n] = o
+				n++
+			}
 		}
 		others = others[:n]
 	}
PATCH

echo "Gold patch applied."
