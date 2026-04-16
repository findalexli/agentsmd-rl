#!/bin/bash
set -e

cd /workspace/hugo

# Idempotency check: check if fix is already applied
if grep -q "Issue #13877" tpl/tplimpl/templatestore.go; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Add "slices" import after "regexp" import in the import block
# Use tab indentation to match gofmt
sed -i '/"regexp"/a\	"slices"' tpl/tplimpl/templatestore.go

# Now replace the template selection logic
# Find the pattern and replace the entire block
sed -i '/\/\/ e.g. \/pages\/home.foo.html and  \/pages\/home.html where foo may be a valid language name in another site./,/return nil, nil/c\
			if d.MediaType != "" \&\& pi.Ext() != nkExisting.PathInfo.Ext() {\n				// Issue #13877: when multiple templates differ only in their file extension\n				// and both extensions are valid suffixes for the same media type,\n				// prefer the one whose extension matches an earlier suffix.\n				if mt, ok := s.opts.MediaTypes.GetByType(d.MediaType); ok {\n					suffixes := mt.Suffixes()\n					newIdx := slices.Index(suffixes, pi.Ext())\n					if newIdx != -1 {\n						existingIdx := slices.Index(suffixes, nkExisting.PathInfo.Ext())\n						if existingIdx == -1 || newIdx < existingIdx {\n							replace = true\n						}\n					}\n				}\n			}\n			if !replace {\n				// e.g. /pages/home.foo.html and  /pages/home.html where foo may be a valid language name in another site.\n				return nil, nil\n			}' tpl/tplimpl/templatestore.go

# Add the test for Issue 13877 to hugolib/template_test.go
# Use printf to avoid extra blank line
cat >> hugolib/template_test.go << 'TESTEOF'

// Issue 13877
func TestTemplateSelectionFirstMediaTypeSuffix(t *testing.T) {
	t.Parallel()

	files := `
-- hugo.toml --
disableKinds = ['home','rss','section','sitemap','taxonomy','term']

[mediaTypes.'text/html']
suffixes = ['b','a','d','c']

[outputFormats.html]
mediaType = 'text/html'
-- content/p1.md --
---
title: p1
---
-- layouts/page.html.a --
page.html.a
-- layouts/page.html.b --
page.html.b
-- layouts/page.html.c --
page.html.c
-- layouts/page.html.d --
page.html.d
`

	b := Test(t, files)

	b.AssertFileContent("public/p1/index.b", "page.html.b")
}
TESTEOF

echo "Gold patch applied successfully"
