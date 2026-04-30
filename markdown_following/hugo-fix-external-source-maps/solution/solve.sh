#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hugo

# Idempotency guard: distinctive line that only exists in the gold patch.
if grep -q "s is already the absolute filename set by the Hugo resolve plugin" \
        internal/js/esbuild/build.go 2>/dev/null; then
    echo "solve.sh: gold patch already applied, skipping"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/internal/js/esbuild/build.go b/internal/js/esbuild/build.go
index cf88276c34b..a3173a22c24 100644
--- a/internal/js/esbuild/build.go
+++ b/internal/js/esbuild/build.go
@@ -225,7 +225,12 @@ func (c *BuildClient) Build(opts Options) (api.BuildResult, error) {
 					}
 					return ss
 				}
-				return ""
+				if strings.HasPrefix(s, opts.OutDir) {
+					// This is an output file, not a source file.
+					return ""
+				}
+				// s is already the absolute filename set by the Hugo resolve plugin.
+				return s
 			}
 			return s
 		}); err != nil {
diff --git a/internal/js/esbuild/sourcemap.go b/internal/js/esbuild/sourcemap.go
index 647f0c0813a..036cab29cbc 100644
--- a/internal/js/esbuild/sourcemap.go
+++ b/internal/js/esbuild/sourcemap.go
@@ -46,7 +46,27 @@ func fixSourceMap(s []byte, resolve func(string) string) ([]byte, error) {
 		return nil, err
 	}

-	sm.Sources = fixSourceMapSources(sm.Sources, resolve)
+	hasSourcesContent := len(sm.SourcesContent) == len(sm.Sources)
+
+	var sources []string
+	var sourcesContent []string
+	for i, src := range sm.Sources {
+		if resolved := resolve(src); resolved != "" {
+			// Absolute filenames works fine on U*ix (tested in Chrome on MacOs), but works very poorly on Windows (again Chrome).
+			// So, convert it to a URL.
+			if u, err := paths.UrlFromFilename(resolved); err == nil {
+				sources = append(sources, u.String())
+				if hasSourcesContent {
+					sourcesContent = append(sourcesContent, sm.SourcesContent[i])
+				}
+			}
+		}
+	}
+
+	sm.Sources = sources
+	if hasSourcesContent {
+		sm.SourcesContent = sourcesContent
+	}

 	b, err := json.Marshal(sm)
 	if err != nil {
@@ -56,20 +76,6 @@ func fixSourceMap(s []byte, resolve func(string) string) ([]byte, error) {
 	return b, nil
 }

-func fixSourceMapSources(s []string, resolve func(string) string) []string {
-	var result []string
-	for _, src := range s {
-		if s := resolve(src); s != "" {
-			// Absolute filenames works fine on U*ix (tested in Chrome on MacOs), but works very poorly on Windows (again Chrome).
-			// So, convert it to a URL.
-			if u, err := paths.UrlFromFilename(s); err == nil {
-				result = append(result, u.String())
-			}
-		}
-	}
-	return result
-}
-
 // Used in tests.
 func SourcesFromSourceMap(s string) []string {
 	var sm sourceMap
PATCH

echo "solve.sh: gold patch applied"
