#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hugo

# Idempotent: skip if already applied
if grep -q 'content := s.ValueAsString()' resources/page/pagemeta/page_frontmatter.go 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/resources/page/pagemeta/page_frontmatter.go b/resources/page/pagemeta/page_frontmatter.go
index b5f9149b763..7c32e89e61a 100644
--- a/resources/page/pagemeta/page_frontmatter.go
+++ b/resources/page/pagemeta/page_frontmatter.go
@@ -555,7 +555,10 @@ func (s Source) ValueAsString() string {
 }

 func (s Source) ValueAsOpenReadSeekCloser() hugio.OpenReadSeekCloser {
-	return hugio.NewOpenReadSeekCloser(hugio.NewReadSeekerNoOpCloserFromString(s.ValueAsString()))
+	content := s.ValueAsString()
+	return func() (hugio.ReadSeekCloser, error) {
+		return hugio.NewReadSeekerNoOpCloserFromString(content), nil
+	}
 }

 // FrontMatterOnlyValues holds values that can only be set via front matter.

PATCH

echo "Patch applied successfully."
