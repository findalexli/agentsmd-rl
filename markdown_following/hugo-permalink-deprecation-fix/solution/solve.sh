#!/bin/bash
set -e

cd /workspace/hugo

# Check if already patched (idempotency check using a distinctive line from the patch)
if grep -q ":contentbasename" hugolib/hugo_sites_multihost_test.go 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/check.sh b/check.sh
index fc7c6849acc..20aacb6eff1 100755
--- a/check.sh
+++ b/check.sh
@@ -52,7 +52,7 @@ run_staticcheck() {
 run_tests() {
     echo "==> Running tests..."
     local output
-    if ! output=$(go test $PACKAGES 2>&1); then
+    if ! output=$(go test -failfast $PACKAGES 2>&1); then
         echo "$output"
         exit 1
     fi
diff --git a/common/hugo/hugo.go b/common/hugo/hugo.go
index 0ac89cbb10b..67932160280 100644
--- a/common/hugo/hugo.go
+++ b/common/hugo/hugo.go
@@ -336,6 +336,8 @@ func deprecateLevel(item, alternative, version string, level logg.Level) {
 func deprecateLevelWithLogger(item, alternative, version string, level logg.Level, log logg.Logger) {
 	var msg string
 	if level == logg.LevelError {
+		// Useful to debug deprecation errors that needs to be removedor fixed. Comment out when done debugging.
+		// hdebug.Panicf("deprecation error: %s was removed in Hugo %s. %s", item, version, alternative)
 		msg = fmt.Sprintf("%s was deprecated in Hugo %s and subsequently removed. %s", item, version, alternative)
 	} else {
 		msg = fmt.Sprintf("%s was deprecated in Hugo %s and will be removed in a future release. %s", item, version, alternative)
diff --git a/hugolib/hugo_modules_test.go b/hugolib/hugo_modules_test.go
index 450e4cbce88..f2f365e50b3 100644
--- a/hugolib/hugo_modules_test.go
+++ b/hugolib/hugo_modules_test.go
@@ -86,7 +86,7 @@ title = "French Title"
 {{ range .Site.RegularPages }}
 |{{ .Title }}|{{ .RelPermalink }}|{{ .Plain }}
 {{ end }}
-{{ $data := .Site.Data }}
+{{ $data := hugo.Data }}
 Data Common: {{ $data.common.value }}
 Data C: {{ $data.c.value }}
 Data D: {{ $data.d.value }}
diff --git a/hugolib/hugo_sites_multihost_test.go b/hugolib/hugo_sites_multihost_test.go
index 875fcfd5a00..a3b3a9ff912 100644
--- a/hugolib/hugo_sites_multihost_test.go
+++ b/hugolib/hugo_sites_multihost_test.go
@@ -20,7 +20,7 @@ enableRobotsTXT = true
 pagerSize = 1

 [permalinks]
-other = "/somewhere/else/:filename"
+other = "/somewhere/else/:contentbasename"

 [taxonomies]
 tag = "tags"
diff --git a/hugolib/page_test.go b/hugolib/page_test.go
index 0d9c9950528..245456b97c3 100644
--- a/hugolib/page_test.go
+++ b/hugolib/page_test.go
@@ -1691,7 +1691,7 @@ func TestPagePathDisablePathToLower(t *testing.T) {
 baseURL = "http://example.com"
 disablePathToLower = true
 [permalinks]
-sect2 = "/:section/:filename/"
+sect2 = "/:section/:contentbasename/"
 sect3 = "/:section/:title/"
 -- content/sect/p1.md --
 ---
diff --git a/hugolib/pagebundler_test.go b/hugolib/pagebundler_test.go
index 7ec749877cc..0ea695366f3 100644
--- a/hugolib/pagebundler_test.go
+++ b/hugolib/pagebundler_test.go
@@ -635,7 +635,7 @@ func TestHTMLFilesIsue11999(t *testing.T) {
 -- hugo.toml --
 disableKinds = ["taxonomy", "term", "rss", "sitemap", "robotsTXT", "404"]
 [permalinks]
-posts = "/myposts/:slugorfilename"
+posts = "/myposts/:slugorcontentbasename"
 -- content/posts/markdown-without-frontmatter.md --
 -- content/posts/html-without-frontmatter.html --
 <html>hello</html>
diff --git a/resources/page/permalinks_integration_test.go b/resources/page/permalinks_integration_test.go
index b33c599a7c7..9406d133c56 100644
--- a/resources/page/permalinks_integration_test.go
+++ b/resources/page/permalinks_integration_test.go
@@ -41,11 +41,11 @@ withallbutlastsectionslug = '/:sectionslugs[:last]/:slug/'
 withsectionslug = '/sectionslug/:sectionslug/:slug/'
 withsectionslugs = '/sectionslugs/:sectionslugs/:slug/'
 [permalinks.section]
-withfilefilename = '/sectionwithfilefilename/:filename/'
+withfilefilename = '/sectionwithfilefilename/:contentbasename/'
 withfilefiletitle = '/sectionwithfilefiletitle/:title/'
 withfileslug = '/sectionwithfileslug/:slug/'
 nofileslug = '/sectionnofileslug/:slug/'
-nofilefilename = '/sectionnofilefilename/:filename/'
+nofilefilename = '/sectionnofilefilename/:contentbasename/'
 nofiletitle1 = '/sectionnofiletitle1/:title/'
 nofiletitle2 = '/sectionnofiletitle2/:sections[:last]/'
 [permalinks.term]
@@ -125,9 +125,12 @@ slug: "mytagslug"
 	b.AssertFileContent("public/pageslug/p1slugvalue/index.html", "Single|page|/pageslug/p1slugvalue/|")
 	b.AssertFileContent("public/sectionslug/section-root-slug/page1-slug/index.html", "Single|page|/sectionslug/section-root-slug/page1-slug/|")
 	b.AssertFileContent("public/sectionslugs/sections-root-slug/level1-slug/page1-slug/index.html", "Single|page|/sectionslugs/sections-root-slug/level1-slug/page1-slug/|")
-	b.AssertFileContent("public/sectionwithfilefilename/index.html", "List|section|/sectionwithfilefilename/|")
+
+	b.AssertFileContent("public/sectionwithfilefilename/withfilefilename/index.html", "List|section|/sectionwithfilefilename/withfilefilename/|")
+
 	b.AssertFileContent("public/sectionwithfileslug/withfileslugvalue/index.html", "List|section|/sectionwithfileslug/withfileslugvalue/|")
-	b.AssertFileContent("public/sectionnofilefilename/index.html", "List|section|/sectionnofilefilename/|")
+
+	b.AssertFileContent("public/sectionnofilefilename/nofilefilename/index.html", "List|section|/sectionnofilefilename/nofilefilename/|")
 	b.AssertFileContent("public/sectionnofileslug/nofileslugs/index.html", "List|section|/sectionnofileslug/nofileslugs/|")
 	b.AssertFileContent("public/sectionnofiletitle1/nofiletitle1s/index.html", "List|section|/sectionnofiletitle1/nofiletitle1s/|")
 	b.AssertFileContent("public/sectionnofiletitle2/index.html", "List|section|/sectionnofiletitle2/|")
@@ -138,7 +141,7 @@ slug: "mytagslug"
 	permalinksConf := b.H.Configs.Base.Permalinks
 	b.Assert(permalinksConf, qt.DeepEquals, map[string]map[string]string{
 		"page":     {"withallbutlastsection": "/:sections[:last]/:slug/", "withallbutlastsectionslug": "/:sectionslugs[:last]/:slug/", "withpageslug": "/pageslug/:slug/", "withsectionslug": "/sectionslug/:sectionslug/:slug/", "withsectionslugs": "/sectionslugs/:sectionslugs/:slug/"},
-		"section":  {"nofilefilename": "/sectionnofilefilename/:filename/", "nofileslug": "/sectionnofileslug/:slug/", "nofiletitle1": "/sectionnofiletitle1/:title/", "nofiletitle2": "/sectionnofiletitle2/:sections[:last]/", "withfilefilename": "/sectionwithfilefilename/:filename/", "withfilefiletitle": "/sectionwithfilefiletitle/:title/", "withfileslug": "/sectionwithfileslug/:slug/"},
+		"section":  {"nofilefilename": "/sectionnofilefilename/:contentbasename/", "nofileslug": "/sectionnofileslug/:slug/", "nofiletitle1": "/sectionnofiletitle1/:title/", "nofiletitle2": "/sectionnofiletitle2/:sections[:last]/", "withfilefilename": "/sectionwithfilefilename/:contentbasename/", "withfilefiletitle": "/sectionwithfilefiletitle/:title/", "withfileslug": "/sectionwithfileslug/:slug/"},
 		"taxonomy": {"tags": "/tagsslug/:slug/"},
 		"term":     {"tags": "/tagsslug/tag/:slug/"},
 	})
@@ -192,7 +195,7 @@ func TestPermalinksNestedSections(t *testing.T) {
 	files := `
 -- hugo.toml --
 [permalinks.page]
-books = '/libros/:sections[1:]/:filename'
+books = '/libros/:sections[1:]/:contentbasename'

 [permalinks.section]
 books = '/libros/:sections[1:]'
PATCH

echo "Patch applied successfully!"
