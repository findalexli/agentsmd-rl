#!/bin/bash
set -euo pipefail

cd /workspace/hugo

# Idempotency: skip if patch already applied.
if grep -q 'Remove invalid entries (e.g. non-taxonomy keys placed inside \[taxonomies\] in TOML)' \
        config/allconfig/alldecoders.go 2>/dev/null; then
    echo "Gold patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index 8bc6860c642..42c0706b637 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -8,6 +8,7 @@
 * Avoid global state at (almost) all cost.
 * This is a project with a long history; assume that a similiar problem has been solved before, look hard for helper functions before creating new ones.
 * In tests, use `qt` matchers (e.g. `b.Assert(err, qt.ErrorMatches, ...)`) instead of raw `if`/`t.Fatal` checks.
+* In tests, always use the latest Hugo specification, e.g. for layouts, it's `layouts/page.html` and not `layouts/_default/single.html`, `layouts/list.html` and not `layouts/_default/list.html`
 * Brevity is good. This applies to code, comments and commit messages. Don't write a novel.
 * Use `./check.sh ./somepackage/...` when iterating.
 * Use `./check.sh` when you're done.
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

echo "Gold patch applied."
