#!/bin/bash
set -euo pipefail

cd /workspace/hugo

if grep -q 'Issue #13877: when multiple templates differ only in their file extension' tpl/tplimpl/templatestore.go 2>/dev/null; then
    echo "Patch already applied — nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/hugolib/template_test.go b/hugolib/template_test.go
index 1a03a41e575..90b8a575af6 100644
--- a/hugolib/template_test.go
+++ b/hugolib/template_test.go
@@ -644,3 +644,35 @@ Overridden.

 	b.AssertFileContent("public/index.html", "Overridden.")
 }
+
+// Issue 13877
+func TestTemplateSelectionFirstMediaTypeSuffix(t *testing.T) {
+	t.Parallel()
+
+	files := `
+-- hugo.toml --
+disableKinds = ['home','rss','section','sitemap','taxonomy','term']
+
+[mediaTypes.'text/html']
+suffixes = ['b','a','d','c']
+
+[outputFormats.html]
+mediaType = 'text/html'
+-- content/p1.md --
+---
+title: p1
+---
+-- layouts/page.html.a --
+page.html.a
+-- layouts/page.html.b --
+page.html.b
+-- layouts/page.html.c --
+page.html.c
+-- layouts/page.html.d --
+page.html.d
+`
+
+	b := Test(t, files)
+
+	b.AssertFileContent("public/p1/index.b", "page.html.b")
+}
diff --git a/tpl/tplimpl/templatestore.go b/tpl/tplimpl/templatestore.go
index 1d4e537fda6..57a0c4f6990 100644
--- a/tpl/tplimpl/templatestore.go
+++ b/tpl/tplimpl/templatestore.go
@@ -29,6 +29,7 @@ import (
 	"path/filepath"
 	"reflect"
 	"regexp"
+	"slices"
 	"sort"
 	"strings"
 	"sync"
@@ -1271,8 +1272,25 @@ func (s *TemplateStore) insertTemplate2(

 	if !replace && existingFound {
 		if len(pi.Identifiers()) >= len(nkExisting.PathInfo.Identifiers()) {
-			// e.g. /pages/home.foo.html and  /pages/home.html where foo may be a valid language name in another site.
-			return nil, nil
+			if d.MediaType != "" && pi.Ext() != nkExisting.PathInfo.Ext() {
+				// Issue #13877: when multiple templates differ only in their file extension
+				// and both extensions are valid suffixes for the same media type,
+				// prefer the one whose extension matches an earlier suffix.
+				if mt, ok := s.opts.MediaTypes.GetByType(d.MediaType); ok {
+					suffixes := mt.Suffixes()
+					newIdx := slices.Index(suffixes, pi.Ext())
+					if newIdx != -1 {
+						existingIdx := slices.Index(suffixes, nkExisting.PathInfo.Ext())
+						if existingIdx == -1 || newIdx < existingIdx {
+							replace = true
+						}
+					}
+				}
+			}
+			if !replace {
+				// e.g. /pages/home.foo.html and  /pages/home.html where foo may be a valid language name in another site.
+				return nil, nil
+			}
 		}
 	}

PATCH

echo "Patch applied."
