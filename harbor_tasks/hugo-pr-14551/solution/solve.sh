#!/bin/bash
set -e

cd /workspace/hugo_repo

# Apply the fix patch
cat <<'PATCH'
diff --git a/config/allconfig/alldecoders.go b/config/allconfig/alldecoders.go
index b7c55258dda..2fb0276d2f9 100644
--- a/config/allconfig/alldecoders.go
+++ b/config/allconfig/alldecoders.go
@@ -335,7 +335,14 @@ var allDecoderSetups = map[string]decodeWeight{
 		key: "taxonomies",
 		decode: func(d decodeWeight, p decodeConfig) error {
 			if p.p.IsSet(d.key) {
-				p.c.Taxonomies = hmaps.CleanConfigStringMapString(p.p.GetStringMapString(d.key))
+				m := hmaps.CleanConfigStringMapString(p.p.GetStringMapString(d.key))
+				// Remove invalid entries (e.g. non-taxonomy keys placed inside [taxonomies] in TOML).
+				for k, v := range m {
+					if k == "" || v == "" {
+						delete(m, k)
+					}
+				}
+				p.c.Taxonomies = m
 			}
 			return nil
 		},
diff --git a/hugolib/disableKinds_test.go b/hugolib/disableKinds_test.go
index 9b02dd4c5f3..a063d891f3e 100644
--- a/hugolib/disableKinds_test.go
+++ b/hugolib/disableKinds_test.go
@@ -334,3 +334,29 @@ title: "Page 2 nn"
 	b.AssertFileExists("public/nn/p1/index.html", false)
 	b.AssertFileExists("public/nn/p2/index.html", false)
 }
+
+// Issue #14550
+// disableKinds = [] after [taxonomies] is inside the taxonomies TOML table,
+// creating a phantom taxonomy that causes .Ancestors to hang.
+func TestDisableKindsEmptySliceAncestors(t *testing.T) {
+	files := `
+-- hugo.toml --
+baseURL = "http://example.com/"
+title = "Bug repro"
+[taxonomies]
+  tag = "tags"
+disableKinds = []
+-- content/posts/hello.md --
+---
+title: Hello
+tags: [demo]
+---
+Hello.
+-- layouts/page.html --
+Ancestors: {{ len .Ancestors }}|{{ range .Ancestors }}{{ .Kind }}|{{ end }}
+-- layouts/list.html --
+{{ .Title }}
+`
+	b := Test(t, files)
+	b.AssertFileContent("public/posts/hello/index.html", "Ancestors: 2|section|home|")
+}
PATCH

git apply --stat <<'PATCH'
diff --git a/config/allconfig/alldecoders.go b/config/allconfig/alldecoders.go
index b7c55258dda..2fb0276d2f9 100644
--- a/config/allconfig/alldecoders.go
+++ b/config/allconfig/alldecoders.go
@@ -335,7 +335,14 @@ var allDecoderSetups = map[string]decodeWeight{
 		key: "taxonomies",
 		decode: func(d decodeWeight, p decodeConfig) error {
 			if p.p.IsSet(d.key) {
-				p.c.Taxonomies = hmaps.CleanConfigStringMapString(p.p.GetStringMapString(d.key))
+				m := hmaps.CleanConfigStringMapString(p.p.GetStringMapString(d.key))
+				// Remove invalid entries (e.g. non-taxonomy keys placed inside [taxonomies] in TOML).
+				for k, v := range m {
+					if k == "" || v == "" {
+						delete(m, k)
+					}
+				}
+				p.c.Taxonomies = m
 			}
 			return nil
 		},
diff --git a/hugolib/disableKinds_test.go b/hugolib/disableKinds_test.go
index 9b02dd4c5f3..a063d891f3e 100644
--- a/hugolib/disableKinds_test.go
+++ b/hugolib/disableKinds_test.go
@@ -334,3 +334,29 @@ title: "Page 2 nn"
 	b.AssertFileExists("public/nn/p1/index.html", false)
 	b.AssertFileExists("public/nn/p2/index.html", false)
 }
+
+// Issue #14550
+// disableKinds = [] after [taxonomies] is inside the taxonomies TOML table,
+// creating a phantom taxonomy that causes .Ancestors to hang.
+func TestDisableKindsEmptySliceAncestors(t *testing.T) {
+	files := `
+-- hugo.toml --
+baseURL = "http://example.com/"
+title = "Bug repro"
+[taxonomies]
+  tag = "tags"
+disableKinds = []
+-- content/posts/hello.md --
+---
+title: Hello
+tags: [demo]
+---
+Hello.
+-- layouts/page.html --
+Ancestors: {{ len .Ancestors }}|{{ range .Ancestors }}{{ .Kind }}|{{ end }}
+-- layouts/list.html --
+{{ .Title }}
+`
+	b := Test(t, files)
+	b.AssertFileContent("public/posts/hello/index.html", "Ancestors: 2|section|home|")
+}
PATCH

git apply <<'PATCH'
diff --git a/config/allconfig/alldecoders.go b/config/allconfig/alldecoders.go
index b7c55258dda..2fb0276d2f9 100644
--- a/config/allconfig/alldecoders.go
+++ b/config/allconfig/alldecoders.go
@@ -335,7 +335,14 @@ var allDecoderSetups = map[string]decodeWeight{
 		key: "taxonomies",
 		decode: func(d decodeWeight, p decodeConfig) error {
 			if p.p.IsSet(d.key) {
-				p.c.Taxonomies = hmaps.CleanConfigStringMapString(p.p.GetStringMapString(d.key))
+				m := hmaps.CleanConfigStringMapString(p.p.GetStringMapString(d.key))
+				// Remove invalid entries (e.g. non-taxonomy keys placed inside [taxonomies] in TOML).
+				for k, v := range m {
+					if k == "" || v == "" {
+						delete(m, k)
+					}
+				}
+				p.c.Taxonomies = m
 			}
 			return nil
 		},
diff --git a/hugolib/disableKinds_test.go b/hugolib/disableKinds_test.go
index 9b02dd4c5f3..a063d891f3e 100644
--- a/hugolib/disableKinds_test.go
+++ b/hugolib/disableKinds_test.go
@@ -334,3 +334,29 @@ title: "Page 2 nn"
 	b.AssertFileExists("public/nn/p1/index.html", false)
 	b.AssertFileExists("public/nn/p2/index.html", false)
 }
+
+// Issue #14550
+// disableKinds = [] after [taxonomies] is inside the taxonomies TOML table,
+// creating a phantom taxonomy that causes .Ancestors to hang.
+func TestDisableKindsEmptySliceAncestors(t *testing.T) {
+	files := `
+-- hugo.toml --
+baseURL = "http://example.com/"
+title = "Bug repro"
+[taxonomies]
+  tag = "tags"
+disableKinds = []
+-- content/posts/hello.md --
+---
+title: Hello
+tags: [demo]
+---
+Hello.
+-- layouts/page.html --
+Ancestors: {{ len .Ancestors }}|{{ range .Ancestors }}{{ .Kind }}|{{ end }}
+-- layouts/list.html --
+{{ .Title }}
+`
+	b := Test(t, files)
+	b.AssertFileContent("public/posts/hello/index.html", "Ancestors: 2|section|home|")
+}
PATCH
