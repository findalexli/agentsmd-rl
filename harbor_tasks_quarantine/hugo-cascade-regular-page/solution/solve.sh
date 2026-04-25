#!/bin/sh
set -e

cd /workspace/hugo

# Check if already patched (idempotency check)
if grep -q "if m.pageConfigSource.Frontmatter != nil {" hugolib/page__meta.go; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/hugolib/page__meta.go b/hugolib/page__meta.go
index 92569e01036..7253be4aa7e 100644
--- a/hugolib/page__meta.go
+++ b/hugolib/page__meta.go
@@ -204,7 +204,7 @@ func (m *pageMetaSource) doInitEarly(h *HugoSites, cascades *page.PageMatcherPar
 		return err
 	}

-	if cnh.isBranchNode(m) && m.pageConfigSource.Frontmatter != nil {
+	if m.pageConfigSource.Frontmatter != nil {
 		if err := m.setCascadeFromMap(m.pageConfigSource.Frontmatter, m.pageConfigSource.SitesMatrix, h.Conf.ConfiguredDimensions(), h.Log); err != nil {
 			return err
 		}
PATCH

echo "Patch applied successfully"
