#!/bin/bash
set -e

cd /workspace/hugo

# Check if already patched (idempotency check)
if grep -q 'KeepNamespaces: \[\]string{"", "x-bind"}' minifiers/config.go; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Use Python for more reliable file editing
python3 << 'EOF'
import re

# Update go.mod
with open('go.mod', 'r') as f:
    content = f.read()
content = content.replace('github.com/tdewolff/minify/v2 v2.24.10', 'github.com/tdewolff/minify/v2 v2.24.11')
content = content.replace('github.com/tdewolff/parse/v2 v2.8.10', 'github.com/tdewolff/parse/v2 v2.8.11')
with open('go.mod', 'w') as f:
    f.write(content)
print("Updated go.mod")

# Update minifiers/config.go
with open('minifiers/config.go', 'r') as f:
    content = f.read()

# Replace the SVG minifier section
old_svg = '''\tSVG: svg.Minifier{
\t\tKeepComments: false,
\t\tPrecision:    0, // 0 means no trimming
\t},'''
new_svg = '''\tSVG: svg.Minifier{
\t\tKeepComments:   false,
\t\tPrecision:      0, // 0 means no trimming
\t\tKeepNamespaces: []string{"", "x-bind"},
\t},'''
content = content.replace(old_svg, new_svg)
with open('minifiers/config.go', 'w') as f:
    f.write(content)
print("Updated minifiers/config.go")

# Update minifiers/minifiers_test.go
with open('minifiers/minifiers_test.go', 'r') as f:
    content = f.read()

# Add the test cases after Issue #13082
old_test = '''\t\t// Issue #13082
\t\t{media.Builtin.HTMLType, "<gcse:searchresults-only></gcse:searchresults-only>", `<gcse:searchresults-only></gcse:searchresults-only>`},'''
new_test = '''\t\t// Issue #13082
\t\t{media.Builtin.HTMLType, "<gcse:searchresults-only></gcse:searchresults-only>", `<gcse:searchresults-only></gcse:searchresults-only>`},
\t\t// Issue #14669.
\t\t{media.Builtin.SVGType, `<use x-bind:href="myicon">`, `<use x-bind:href="myicon">`},
\t\t{media.Builtin.SVGType, `<use :href="myicon">`, `<use :href="myicon">`},'''
content = content.replace(old_test, new_test)
with open('minifiers/minifiers_test.go', 'w') as f:
    f.write(content)
print("Updated minifiers/minifiers_test.go")

print("All files updated successfully")
EOF

# Update go modules after patch
go mod tidy

echo "Patch applied successfully"
