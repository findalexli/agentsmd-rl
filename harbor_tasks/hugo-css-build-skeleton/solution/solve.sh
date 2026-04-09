#!/bin/bash
set -e

cd /workspace/hugo

# Apply the gold patch from PR #14631
cat <<'PATCH' | git apply -
diff --git a/create/skeletons/theme/assets/css/components/footer.css b/create/skeletons/theme/assets/css/components/footer.css
new file mode 100644
index 00000000000..abe2b5a6e7d
--- /dev/null
+++ b/create/skeletons/theme/assets/css/components/footer.css
@@ -0,0 +1,4 @@
+footer {
+  border-top: 1px solid #222;
+  margin-top: 1rem;
+}
diff --git a/create/skeletons/theme/assets/css/components/header.css b/create/skeletons/theme/assets/css/components/header.css
new file mode 100644
index 00000000000..8efea1e8c92
--- /dev/null
+++ b/create/skeletons/theme/assets/css/components/header.css
@@ -0,0 +1,4 @@
+header {
+  border-bottom: 1px solid #222;
+  margin-bottom: 1rem;
+}
diff --git a/create/skeletons/theme/assets/css/main.css b/create/skeletons/theme/assets/css/main.css
index 166ade92452..6c0b6609068 100644
--- a/create/skeletons/theme/assets/css/main.css
+++ b/create/skeletons/theme/assets/css/main.css
@@ -1,3 +1,6 @@
+@import "components/header.css";
+@import "components/footer.css";
+
 body {
   color: #222;
   font-family: sans-serif;
   line-height: 1.5;
@@ -6,16 +9,6 @@ body {
   max-width: 768px;
 }

-header {
-  border-bottom: 1px solid #222;
-  margin-bottom: 1rem;
-}
-
-footer {
-  border-top: 1px solid #222;
-  margin-top: 1rem;
-}
-
 a {
   color: #00e;
   text-decoration: none;
diff --git a/create/skeletons/theme/layouts/_partials/head/css.html b/create/skeletons/theme/layouts/_partials/head/css.html
index d76d23a16ce..889786684b1 100644
--- a/create/skeletons/theme/layouts/_partials/head/css.html
+++ b/create/skeletons/theme/layouts/_partials/head/css.html
@@ -1,9 +1,15 @@
 {{- with resources.Get "css/main.css" }}
-  {{- if hugo.IsDevelopment }}
-    <link rel="stylesheet" href="{{ .RelPermalink }}">
-  {{- else }}
-    {{- with . | minify | fingerprint }}
-      <link rel="stylesheet" href="{{ .RelPermalink }}" integrity="{{ .Data.Integrity }}" crossorigin="anonymous">
+  {{- $opts := dict
+    "minify" (cond hugo.IsDevelopment false true)
+    "sourceMap" (cond hugo.IsDevelopment "linked" "none")
+  }}
+  {{- with . | css.Build $opts }}
+    {{- if hugo.IsDevelopment }}
+      <link rel="stylesheet" href="{{ .RelPermalink }}">
+    {{- else }}
+      {{- with . | fingerprint }}
+        <link rel="stylesheet" href="{{ .RelPermalink }}" integrity="{{ .Data.Integrity }}" crossorigin="anonymous">
+      {{- end }}
     {{- end }}
   {{- end }}
 {{- end }}
diff --git a/create/skeletons/theme/layouts/_partials/head/js.html b/create/skeletons/theme/layouts/_partials/head/js.html
index 16ffbedfeaa..0210efa8b42 100644
--- a/create/skeletons/theme/layouts/_partials/head/js.html
+++ b/create/skeletons/theme/layouts/_partials/head/js.html
@@ -1,8 +1,7 @@
 {{- with resources.Get "js/main.js" }}
   {{- $opts := dict
-    "minify" (not hugo.IsDevelopment)
-    "sourceMap" (cond hugo.IsDevelopment "external" "")
-    "targetPath" "js/main.js"
+    "minify" (cond hugo.IsDevelopment false true)
+    "sourceMap" (cond hugo.IsDevelopment "linked" "none")
   }}
   {{- with . | js.Build $opts }}
     {{- if hugo.IsDevelopment }}
       <script src="{{ .RelPermalink }}"></script>
     {{- else }}
       {{- with . | fingerprint }}
         <script src="{{ .RelPermalink }}" integrity="{{ .Data.Integrity }}" crossorigin="anonymous"></script>
       {{- end }}
     {{- end }}
   {{- end }}
{{- end }}
PATCH

echo "Patch applied successfully"
