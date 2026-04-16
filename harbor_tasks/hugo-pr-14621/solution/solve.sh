#!/bin/bash
set -e

cd /workspace/hugo

# Check if patch is already applied (idempotency check)
if grep -q "defaultCSSFileLoaderExts" internal/js/esbuild/resolve.go 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Use Python to apply the patches reliably
python3 << 'PYTHONPATCH'
import re

# Patch 1: Add defaultCSSFileLoaderExts to resolve.go
with open('internal/js/esbuild/resolve.go', 'r') as f:
    resolve_content = f.read()

# Find the extensionToLoaderMapCSS and add after it
new_resolve_section = '''var extensionToLoaderMapCSS = map[string]api.Loader{
	".css": api.LoaderCSS,
}

// Common static file extensions that should use the file loader in CSS builds.
var defaultCSSFileLoaderExts = []string{
	".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif",
	".woff", ".woff2", ".ttf", ".eot", ".otf",
}'''

resolve_content = resolve_content.replace(
    '''var extensionToLoaderMapCSS = map[string]api.Loader{
	".css": api.LoaderCSS,
}''',
    new_resolve_section
)

with open('internal/js/esbuild/resolve.go', 'w') as f:
    f.write(resolve_content)

print("Patched resolve.go")

# Patch 2: Modify options.go
with open('internal/js/esbuild/options.go', 'r') as f:
    options_content = f.read()

# Add the CSS default loaders block after the loaders configuration
old_loaders_block = '''\tif opts.Loaders != nil {
\t\tloaders = make(map[string]api.Loader)
\t\tfor k, v := range opts.Loaders {
\t\t\tloader, found := nameLoader[v]
\t\t\tif !found {
\t\t\t\terr = fmt.Errorf("invalid loader: %q", v)
\t\t\t\treturn
\t\t\t}
\t\t\tloaders[k] = loader
\t\t}
\t}

\tmediaType'''

new_loaders_block = '''\tif opts.Loaders != nil {
\t\tloaders = make(map[string]api.Loader)
\t\tfor k, v := range opts.Loaders {
\t\t\tloader, found := nameLoader[v]
\t\t\tif !found {
\t\t\t\terr = fmt.Errorf("invalid loader: %q", v)
\t\t\t\treturn
\t\t\t}
\t\t\tloaders[k] = loader
\t\t}
\t} else if opts.IsCSS {
\t\tloaders = make(map[string]api.Loader)
\t\t// For CSS builds, default to the file loader for common static
\t\t// file extensions so that url() references are handled correctly
\t\t// even when resolved by ESBuild's native resolver.
\t\t// See #14619.
\t\tfor _, ext := range defaultCSSFileLoaderExts {
\t\t\tloaders[ext] = api.LoaderFile
\t\t}
\t}

\tmediaType'''

options_content = options_content.replace(old_loaders_block, new_loaders_block)

# Fix loaderFromFilename - remove unconditional LoaderFile return for CSS
old_css_loader = '''\tif o.IsCSS {
\t\tl, found := extensionToLoaderMapCSS[ext]
\t\tif found {
\t\t\treturn l
\t\t}
\t\t// For CSS builds, handling, default to the file loader for unknown extensions.
\t\treturn api.LoaderFile
\t}'''

new_css_loader = '''\tif o.IsCSS {
\t\tl, found := extensionToLoaderMapCSS[ext]
\t\tif found {
\t\t\treturn l
\t\t}
\t}'''

options_content = options_content.replace(old_css_loader, new_css_loader)

# Change final return from LoaderJS to LoaderDefault
options_content = options_content.replace(
    '''\t}\n\n\treturn api.LoaderJS\n}''',
    '''\t}\n\n\treturn api.LoaderDefault\n}'''
)

with open('internal/js/esbuild/options.go', 'w') as f:
    f.write(options_content)

print("Patched options.go")

# Patch 3: Add test case to build_integration_test.go
with open('tpl/css/build_integration_test.go', 'r') as f:
    test_content = f.read()

# Add static file after pixel.png
old_png = '''-- assets/a/pixel.png --
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
-- assets/css/main.css --'''

new_png = '''-- assets/a/pixel.png --
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
-- static/b/issue14619.png --
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
-- assets/css/main.css --'''

test_content = test_content.replace(old_png, new_png)

# Add CSS rule for static file
old_css = '''body {
  background-image: url("a/pixel.png");
}
-- layouts/home.html --'''

new_css = '''body {
  background-image: url("a/pixel.png");
}
div {
  background-image: url("static/b/issue14619.png");
}
-- layouts/home.html --'''

test_content = test_content.replace(old_css, new_css)

# Add assertions
old_assert = '''b.AssertFileContent("public/css/main.css", `./pixel-NJRUOINY.png`)
\tb.AssertFileExists("public/css/pixel-NJRUOINY.png", true)
}'''

new_assert = '''b.AssertFileContent("public/css/main.css", `./pixel-NJRUOINY.png`)
\tb.AssertFileExists("public/css/pixel-NJRUOINY.png", true)
\tb.AssertFileContent("public/css/main.css", `url("./issue14619-NJRUOINY.png")`)
\tb.AssertFileExists("public/css/issue14619-NJRUOINY.png", true)
}'''

test_content = test_content.replace(old_assert, new_assert)

with open('tpl/css/build_integration_test.go', 'w') as f:
    f.write(test_content)

print("Patched build_integration_test.go")
print("All patches applied successfully!")
PYTHONPATCH

echo "Patch applied successfully."
