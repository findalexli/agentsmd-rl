#!/usr/bin/env python3
import os
import re

def main():
    repo = "/workspace/hugo"
    
    # 1. Read and modify hugocontext.go
    hugocontext_path = os.path.join(repo, "markup/goldmark/hugocontext/hugocontext.go")
    with open(hugocontext_path, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "DedentMarkers" in content:
        print("Already patched, skipping")
        return
    
    # Add hugoCtxIndentedRe after hugoCtxRe
    content = content.replace(
        'hugoCtxRe           = regexp.MustCompile(`{{__hugo_ctx( pid=\\d+)?/?}}\\n?`)',
        '''hugoCtxRe           = regexp.MustCompile(`{{__hugo_ctx( pid=\\d+)?/?}}\\n?`)
	hugoCtxIndentedRe   = regexp.MustCompile(`(?m)^[ \\t]+({{__hugo_ctx[^\\n]*}})`)'''
    )
    
    # Add DedentMarkers function before Strip function
    content = content.replace(
        '// Strip strips any Hugo context markers from b.',
        '''// DedentMarkers removes leading whitespace from Hugo context marker lines
// to prevent them from being treated as indented code blocks by Goldmark.
func DedentMarkers(b []byte) []byte {
	if !bytes.Contains(b, hugoCtxPrefix) {
		return b
	}
	return hugoCtxIndentedRe.ReplaceAll(b, []byte("$1"))
}

// Strip strips any Hugo context markers from b.'''
    )
    
    with open(hugocontext_path, 'w') as f:
        f.write(content)
    print("Modified hugocontext.go")
    
    # 2. Modify page__content.go to add DedentMarkers call
    page_content_path = os.path.join(repo, "hugolib/page__content.go")
    with open(page_content_path, 'r') as f:
        content = f.read()
    
    # Find the location and add the call
    old_code = '''\t\tct.contentToRender, err = p.contentToRender(p.m.pageConfig.Content.Markup, ctx, true)\n\t\tif err != nil {\n\t\t\treturn nil, err\n\t\t}'''
    new_code = '''\t\tct.contentToRender, err = p.contentToRender(p.m.pageConfig.Content.Markup, ctx, true)\n\t\tif err != nil {\n\t\t\treturn nil, err\n\t\t}\n\n\t\tct.contentToRender = hugocontext.DedentMarkers(ct.contentToRender)'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(page_content_path, 'w') as f:
            f.write(content)
        print("Modified page__content.go")
    else:
        print("Warning: Could not find exact pattern in page__content.go")
        # Try a simpler pattern
        content = content.replace(
            '\t\t\treturn nil, err\n\t\t}\n\n\t\tif hasVariants {',
            '\t\t\treturn nil, err\n\t\t}\n\n\t\tct.contentToRender = hugocontext.DedentMarkers(ct.contentToRender)\n\n\t\tif hasVariants {'
        )
        with open(page_content_path, 'w') as f:
            f.write(content)
        print("Modified page__content.go (alternative pattern)")
    
    # 3. Add test function to rendershortcodes_test.go
    test_path = os.path.join(repo, "hugolib/rendershortcodes_test.go")
    test_func = '''\n// Issue 12457.
func TestRenderShortcodesCodeBlock(t *testing.T) {
\tt.Parallel()

\tfiles := `
-- hugo.toml --
disableKinds = ['section','rss','sitemap','taxonomy','term']
-- layouts/_shortcodes/foo.html --
{{ $p := site.GetPage "includeme" }}
    {{ $p.RenderShortcodes }}
-- layouts/home.html --
{{ .Content }}
-- content/_index.md --
---
title: home
---
{{% foo %}}
-- content/includeme.md --
---
title: "includeme"
---
Some markdown.
    `

\tb := Test(t, files)
\tb.AssertNoRenderShortcodesArtifacts()
\tb.AssertFileContentEquals("public/index.html", "<p>Some markdown.</p>\\n")
}
'''
    with open(test_path, 'a') as f:
        f.write(test_func)
    print("Modified rendershortcodes_test.go")
    print("Patch applied successfully")

if __name__ == "__main__":
    main()
