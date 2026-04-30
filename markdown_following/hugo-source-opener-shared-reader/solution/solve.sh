#!/bin/bash
set -euo pipefail

cd /workspace/hugo

# Idempotency: skip if patch already applied.
if grep -q 'return func() (hugio.ReadSeekCloser, error)' resources/page/pagemeta/page_frontmatter.go 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/hugolib/pagesfromdata/pagesfromgotmpl_integration_test.go b/hugolib/pagesfromdata/pagesfromgotmpl_integration_test.go
index 30b6cab3372..2b3aa6e29db 100644
--- a/hugolib/pagesfromdata/pagesfromgotmpl_integration_test.go
+++ b/hugolib/pagesfromdata/pagesfromgotmpl_integration_test.go
@@ -893,3 +893,29 @@ baseURL = "https://example.com"
 	// _content.gotmpl which was siblings of index.md (leaf bundles) was mistakingly classified as a content resource.
 	hugolib.Test(t, files)
 }
+
+// Issue 14684
+func TestPagesFromGoTmplAddResourceFromStringContent(t *testing.T) {
+	t.Parallel()
+
+	files := `
+-- hugo.toml --
+disableKinds = ["taxonomy", "term", "rss", "sitemap"]
+baseURL = "https://example.com"
+-- assets/a/pixel.png --
+iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
+-- layouts/single.html --
+{{ with .Resources.Get "pixel.png" }}
+{{ with .Resize "1x1" }}Resized: {{ .Width }}x{{ .Height }}|{{ end }}
+{{ end }}
+-- content/_content.gotmpl --
+{{ $pixel := resources.Get "a/pixel.png" }}
+{{ $content := dict "mediaType" $pixel.MediaType.Type "value" $pixel.Content }}
+{{ $.AddPage (dict "path" "p1" "title" "p1") }}
+{{ $.AddResource (dict "path" "p1/pixel.png" "content" $content) }}
+`
+
+	b := hugolib.Test(t, files)
+
+	b.AssertFileContent("public/p1/index.html", "Resized: 1x1|")
+}
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
diff --git a/resources/page/pagemeta/page_frontmatter_test.go b/resources/page/pagemeta/page_frontmatter_test.go
index 39074ee15f2..d99d75248b0 100644
--- a/resources/page/pagemeta/page_frontmatter_test.go
+++ b/resources/page/pagemeta/page_frontmatter_test.go
@@ -14,6 +14,7 @@
 package pagemeta_test

 import (
+	"io"
 	"strings"
 	"testing"
 	"time"
@@ -154,6 +155,39 @@ func TestFrontMatterDatesDefaultKeyword(t *testing.T) {
 	c.Assert(d.PageConfigLate.Dates.ExpiryDate.IsZero(), qt.Equals, true)
 }

+// Issue 14684
+// Each call to the opener must return an independent reader. With the old
+// implementation, opener() returned the same shared reader seeked to 0, so a
+// second open would reset the position of a reader already in use.
+func TestSourceValueAsOpenReadSeekCloserIsIndependent(t *testing.T) {
+	c := qt.New(t)
+	s := pagemeta.Source{Value: "abcdefgh"}
+	opener := s.ValueAsOpenReadSeekCloser()
+
+	r1, err := opener()
+	c.Assert(err, qt.IsNil)
+	defer r1.Close()
+
+	// Partially consume r1.
+	buf := make([]byte, 4)
+	_, err = io.ReadFull(r1, buf)
+	c.Assert(err, qt.IsNil)
+	c.Assert(string(buf), qt.Equals, "abcd")
+
+	// Open a second reader and fully consume it.
+	r2, err := opener()
+	c.Assert(err, qt.IsNil)
+	defer r2.Close()
+	all, err := io.ReadAll(r2)
+	c.Assert(err, qt.IsNil)
+	c.Assert(string(all), qt.Equals, "abcdefgh")
+
+	// r1's position must be unaffected; it should yield the remaining half.
+	rest, err := io.ReadAll(r1)
+	c.Assert(err, qt.IsNil)
+	c.Assert(string(rest), qt.Equals, "efgh")
+}
+
 func TestContentMediaTypeFromMarkup(t *testing.T) {
 	c := qt.New(t)
 	logger := loggers.NewDefault()
PATCH

echo "Patch applied."
