#!/bin/bash
set -e

cd /workspace/hugo

# Apply the gold patch for PR #14622: Fix external source maps
# First try git apply, then patch, then manual

cat << 'ENDPATCH' | git apply --3way - 2>/dev/null || true
diff --git a/internal/js/esbuild/build.go b/internal/js/esbuild/build.go
index cf88276c34b..a3173a22c24 100644
--- a/internal/js/esbuild/build.go
+++ b/internal/js/esbuild/build.go
@@ -225,7 +225,12 @@ func (c *BuildClient) Build(opts Options) (api.BuildResult, error) {
 				}
 				return ss
 			}
-			return ""
+			if strings.HasPrefix(s, opts.OutDir) {
+				// This is an output file, not a source file.
+				return ""
+			}
+			// s is already the absolute filename set by the Hugo resolve plugin.
+			return s
 		}
 		return s
 	}); err != nil {
ENDPATCH

# Verify and manually fix build.go if needed
python3 << 'PYEOF'
import re

with open('internal/js/esbuild/build.go', 'r') as f:
    content = f.read()

# Check if the fix is already correctly applied
if "if strings.HasPrefix(s, opts.OutDir)" in content and "// s is already the absolute filename set by the Hugo resolve plugin" in content:
    print("build.go already has the fix")
else:
    print("Manually applying fix to build.go...")

    # The fix needs to replace:
    #   }
    #   return ""
    # }
    # return s
    # (at the end of isNsHugo block)
    # with:
    #   }
    #   if strings.HasPrefix(s, opts.OutDir) {
    #       // This is an output file, not a source file.
    #       return ""
    #   }
    #   // s is already the absolute filename set by the Hugo resolve plugin.
    #   return s
    # }
    # return s

    # Find and fix the pattern
    old_pattern = '''\t\t\t\treturn ss
\t\t\t\t}
\t\t\t\treturn ""
\t\t\t}
\t\t\treturn s'''

    new_pattern = '''\t\t\t\treturn ss
\t\t\t\t}
\t\t\t\tif strings.HasPrefix(s, opts.OutDir) {
\t\t\t\t\t// This is an output file, not a source file.
\t\t\t\t\treturn ""
\t\t\t\t}
\t\t\t\t// s is already the absolute filename set by the Hugo resolve plugin.
\t\t\t\treturn s
\t\t\t}
\t\t\treturn s'''

    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        with open('internal/js/esbuild/build.go', 'w') as f:
            f.write(content)
        print("build.go fixed successfully")
    else:
        print("ERROR: Could not find the pattern to replace in build.go")
        # Print some context for debugging
        idx = content.find('return ss')
        if idx > 0:
            print("Found 'return ss' at position", idx)
            print("Context:", repr(content[idx:idx+100]))
PYEOF

# Apply sourcemap.go changes if not already applied
python3 << 'PYEOF'
with open('internal/js/esbuild/sourcemap.go', 'r') as f:
    content = f.read()

if "hasSourcesContent := len(sm.SourcesContent) == len(sm.Sources)" in content:
    print("sourcemap.go already has the fix")
else:
    print("Applying fix to sourcemap.go...")

    # Replace fixSourceMap function body
    old_code = '''\tsm.Sources = fixSourceMapSources(sm.Sources, resolve)

\tb, err := json.Marshal(sm)'''

    new_code = '''\thasSourcesContent := len(sm.SourcesContent) == len(sm.Sources)

\tvar sources []string
\tvar sourcesContent []string
\tfor i, src := range sm.Sources {
\t\tif resolved := resolve(src); resolved != "" {
\t\t\t// Absolute filenames works fine on U*ix (tested in Chrome on MacOs), but works very poorly on Windows (again Chrome).
\t\t\t// So, convert it to a URL.
\t\t\tif u, err := paths.UrlFromFilename(resolved); err == nil {
\t\t\t\tsources = append(sources, u.String())
\t\t\t\tif hasSourcesContent {
\t\t\t\t\tsourcesContent = append(sourcesContent, sm.SourcesContent[i])
\t\t\t\t}
\t\t\t}
\t\t}
\t}

\tsm.Sources = sources
\tif hasSourcesContent {
\t\tsm.SourcesContent = sourcesContent
\t}

\tb, err := json.Marshal(sm)'''

    if old_code in content:
        content = content.replace(old_code, new_code)
    else:
        print("WARNING: Could not find sourcemap.go pattern 1")

    # Remove fixSourceMapSources function
    old_func = '''\nfunc fixSourceMapSources(s []string, resolve func(string) string) []string {
\tvar result []string
\tfor _, src := range s {
\t\tif s := resolve(src); s != "" {
\t\t\t// Absolute filenames works fine on U*ix (tested in Chrome on MacOs), but works very poorly on Windows (again Chrome).
\t\t\t// So, convert it to a URL.
\t\t\tif u, err := paths.UrlFromFilename(s); err == nil {
\t\t\t\tresult = append(result, u.String())
\t\t\t}
\t\t}
\t}
\treturn result
}
'''

    if old_func in content:
        content = content.replace(old_func, '\n')
    else:
        print("WARNING: Could not find sourcemap.go pattern 2")

    with open('internal/js/esbuild/sourcemap.go', 'w') as f:
        f.write(content)
    print("sourcemap.go fixed")
PYEOF

# Fix JS integration test
sed -i 's/checkMap("public\/js\/main.js.map", 4)/checkMap("public\/js\/main.js.map", 5)/' resources/resource_transformers/js/js_integration_test.go

# Fix CSS integration test
python3 << 'PYEOF'
with open('tpl/css/build_integration_test.go', 'r') as f:
    content = f.read()

# Add imports
old_imports = '''import (
\t"strings"
\t"testing"

\t"github.com/gohugoio/hugo/htesting"
\t"github.com/gohugoio/hugo/hugolib"
)'''

new_imports = '''import (
\t"strings"
\t"testing"

\tqt "github.com/frankban/quicktest"
\t"github.com/gohugoio/hugo/htesting"
\t"github.com/gohugoio/hugo/hugolib"
\t"github.com/gohugoio/hugo/internal/js/esbuild"
)'''

if 'qt "github.com/frankban/quicktest"' not in content:
    content = content.replace(old_imports, new_imports)

# Update template placeholder
content = content.replace('"minify" false', '"minify" MINIFY')

# Replace the old test loop with the new one
old_test = '''\tr := strings.NewReplacer(
\t\t"SOURCE_MAP", "linked",
\t\t"SOURCES_CONTENT", "true",
\t)

\tfiles := r.Replace(filesTemplate)

\tb := hugolib.Test(t, files, hugolib.TestOptOsFs())
\tb.AssertFileContent("public/css/main.css", "/*# sourceMappingURL=main.css.map */")
\tb.AssertFileContent("public/css/main.css.map",
\t\t`"sourcesContent":["p { background: red; }"`,
\t\t"AAAA;AAAI,cAAY;AAAK",
\t)'''

new_test = '''\tvar (
\t\tr     *strings.Replacer
\t\tfiles string
\t\tb     *hugolib.IntegrationTestBuilder
\t)

\tfor _, minify := range []string{"true", "false"} {

\t\tr = strings.NewReplacer(
\t\t\t"SOURCE_MAP", "linked",
\t\t\t"SOURCES_CONTENT", "true",
\t\t\t"MINIFY", minify,
\t\t)

\t\tfiles = r.Replace(filesTemplate)

\t\tb = hugolib.Test(t, files, hugolib.TestOptOsFs())
\t\tb.AssertFileContent("public/css/main.css", "/*# sourceMappingURL=main.css.map */")
\t\tb.AssertFileContent("public/css/main.css.map",
\t\t\t`"sourcesContent":["`,
\t\t\t`"mappings":"`,
\t\t)

\t\tsources := esbuild.SourcesFromSourceMap(b.FileContent("public/css/main.css.map"))
\t\t// main.css + foo.css + bar.css + baz.css = 4 sources.
\t\tb.Assert(len(sources), qt.Equals, 4)
\t}'''

if old_test in content:
    content = content.replace(old_test, new_test)
else:
    print("WARNING: Could not find CSS test pattern")

# Add MINIFY to other test cases
content = content.replace(
    '''\tr = strings.NewReplacer(
\t\t"SOURCE_MAP", "external",
\t\t"SOURCES_CONTENT", "true",
\t)''',
    '''\tr = strings.NewReplacer(
\t\t"SOURCE_MAP", "external",
\t\t"SOURCES_CONTENT", "true",
\t\t"MINIFY", "false",
\t)''')

content = content.replace(
    '''\tr = strings.NewReplacer(
\t\t"SOURCE_MAP", "external",
\t\t"SOURCES_CONTENT", "false",
\t)''',
    '''\tr = strings.NewReplacer(
\t\t"SOURCE_MAP", "external",
\t\t"SOURCES_CONTENT", "false",
\t\t"MINIFY", "false",
\t)''')

content = content.replace(
    '''\tr = strings.NewReplacer(
\t\t"SOURCE_MAP", "inline",
\t\t"SOURCES_CONTENT", "false",
\t)''',
    '''\tr = strings.NewReplacer(
\t\t"SOURCE_MAP", "inline",
\t\t"SOURCES_CONTENT", "false",
\t\t"MINIFY", "false",
\t)''')

with open('tpl/css/build_integration_test.go', 'w') as f:
    f.write(content)
PYEOF

# Verify all fixes are applied
echo "Verifying fixes..."
grep -q "if strings.HasPrefix(s, opts.OutDir)" internal/js/esbuild/build.go || { echo "ERROR: build.go fix missing"; exit 1; }
grep -q "hasSourcesContent := len(sm.SourcesContent) == len(sm.Sources)" internal/js/esbuild/sourcemap.go || { echo "ERROR: sourcemap.go fix missing"; exit 1; }
grep -q "checkMap(\"public/js/main.js.map\", 5)" resources/resource_transformers/js/js_integration_test.go || { echo "ERROR: JS test fix missing"; exit 1; }
grep -q "qt \"github.com/frankban/quicktest\"" tpl/css/build_integration_test.go || { echo "ERROR: CSS test imports missing"; exit 1; }
grep -q "for _, minify := range" tpl/css/build_integration_test.go || { echo "ERROR: CSS test loop missing"; exit 1; }

# Fix formatting issues introduced by our patches
gofmt -w internal/js/esbuild/sourcemap.go

echo "All patches applied successfully!"
