#!/bin/bash
set -e

cd /workspace/hugo

# Apply the fix: Update tdewolff/minify and add KeepNamespaces to SVG minifier config
# This fixes issue #14669 where Alpine.js directives (x-bind, :) were being stripped from SVGs

patch -p1 <<'PATCH'
diff --git a/go.mod b/go.mod
index 75815e41c14..964636826f3 100644
--- a/go.mod
+++ b/go.mod
@@ -66,8 +66,8 @@ require (
 	github.com/spf13/cobra v1.10.2
 	github.com/spf13/fsync v0.10.1
 	github.com/spf13/pflag v1.0.10
-	github.com/tdewolff/minify/v2 v2.24.10
-	github.com/tdewolff/parse/v2 v2.8.10
+	github.com/tdewolff/minify/v2 v2.24.11
+	github.com/tdewolff/parse/v2 v2.8.11
 	github.com/tetratelabs/wazero v1.11.0
 	github.com/yuin/goldmark v1.7.17
 	github.com/yuin/goldmark-emoji v1.0.6

diff --git a/minifiers/config.go b/minifiers/config.go
index 35d40ac249e..aab19b6af23 100644
--- a/minifiers/config.go
+++ b/minifiers/config.go
@@ -46,8 +46,9 @@ var defaultTdewolffConfig = TdewolffConfig{
 	},
 	JSON: json.Minifier{},
 	SVG: svg.Minifier{
-		KeepComments: false,
-		Precision:    0, // 0 means no trimming
+		KeepComments:   false,
+		Precision:      0, // 0 means no trimming
+		KeepNamespaces: []string{"", "x-bind"},
 	},
 	XML: xml.Minifier{
 		KeepWhitespace: false,
PATCH

# Download the updated module
go mod download github.com/tdewolff/minify/v2 github.com/tdewolff/parse/v2

# Idempotency check: verify the distinctive line exists
grep -q 'KeepNamespaces: \[\]string{"", "x-bind"}' minifiers/config.go || exit 1

echo "Fix applied successfully"
