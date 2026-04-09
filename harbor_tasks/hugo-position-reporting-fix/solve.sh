#!/bin/bash
set -e

cd /workspace/hugo

# Check if patch is already applied (idempotency check)
if grep -q "type sourceInfo struct" hugolib/page__content.go; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat << 'PATCH' | git apply -
diff --git a/hugolib/page__content.go b/hugolib/page__content.go
index 63c97305083..7377936f309 100644
--- a/hugolib/page__content.go
+++ b/hugolib/page__content.go
@@ -457,6 +457,17 @@ type contentTableOfContents struct {
 	contentPlaceholders map[string]shortcodeRenderer

 	contentToRender []byte
+
+	sourceInfo
+}
+
+type sourceInfo struct {
+	// Optional override for the filename used in position reporting.
+	filename string
+	// The original source bytes.
+	source []byte
+	// Maps positions in the content sent to Goldmark back to the original source.
+	sourceMap []sourceMapEntry
 }

 type contentSummary struct {
@@ -515,7 +526,7 @@ func (c *cachedContentScope) contentRendered(ctx context.Context) (contentSummar

 		if ct.astDoc != nil {
 			// The content is parsed, but not rendered.
-			r, ok, err := po.contentRenderer.RenderContent(ctx, ct.contentToRender, ct.astDoc)
+			r, ok, err := po.contentRenderer.RenderContent(ctx, ct.contentToRender, ct.sourceInfo, ct.astDoc)
 			if err != nil {
 				return nil, err
 			}
@@ -638,12 +649,13 @@ func (c *cachedContentScope) contentToC(ctx context.Context) (contentTableOfCont
 	versionv := c.version(cp)

 	v, err := c.pm.contentTableOfContents.GetOrCreate(key, func(string) (*resources.StaleValue[contentTableOfContents], error) {
-		source, err := c.pi.contentSource(c)
+		var err error
+		var ct contentTableOfContents
+		ct.source, err = c.pi.contentSource(c)
 		if err != nil {
 			return nil, err
 		}

-		var ct contentTableOfContents
 		if err := cp.initRenderHooks(); err != nil {
 			return nil, err
 		}
@@ -678,7 +690,7 @@ func (c *cachedContentScope) contentToC(ctx context.Context) (contentTableOfCont
 		ctx = setGetContentCallbackInContext.Set(ctx, ctxCallback)

 		var hasVariants bool
-		ct.contentToRender, cp.sourceMap, hasVariants, err = c.pi.contentToRender(ctx, source, ct.contentPlaceholders)
+		ct.contentToRender, ct.sourceMap, hasVariants, err = c.pi.contentToRender(ctx, ct.source, ct.contentPlaceholders)
 		if err != nil {
 			return nil, err
 		}
@@ -926,9 +938,15 @@ func (c *cachedContentScope) RenderString(ctx context.Context, args ...any) (tem
 	}

 	if pageparser.HasShortcode(contentToRender) {
-		contentToRenderb := []byte(contentToRender)
+		ct := contentTableOfContents{
+			sourceInfo: sourceInfo{
+				filename: pco.po.p.pathOrTitle() + " (rendered from string)",
+				source:   []byte(contentToRender),
+			},
+		}
+		ct.contentToRender = ct.source
 		// String contains a shortcode.
-		parseInfo.itemsStep1, err = pageparser.ParseBytes(contentToRenderb, pageparser.Config{
+		parseInfo.itemsStep1, err = pageparser.ParseBytes(ct.source, pageparser.Config{
 			NoFrontMatter:    true,
 			NoSummaryDivider: true,
 		})
@@ -937,7 +955,7 @@ func (c *cachedContentScope) RenderString(ctx context.Context, args ...any) (tem
 		}

 		parseInfo.shortcodeParseInfo = newShortcodeHandler(pco.po.p.pathOrTitle(), pco.po.p.s.h.Deps)
-		if err := parseInfo.parseSource(contentToRenderb, true); err != nil {
+		if err := parseInfo.parseSource(ct.source, true); err != nil {
 			return "", err
 		}

@@ -946,14 +964,15 @@ func (c *cachedContentScope) RenderString(ctx context.Context, args ...any) (tem
 			return "", err
 		}

-		contentToRender, _, hasVariants, err := parseInfo.contentToRender(ctx, contentToRenderb, placeholders)
+		var hasVariants bool
+		ct.contentToRender, ct.sourceMap, hasVariants, err = parseInfo.contentToRender(ctx, ct.source, placeholders)
 		if err != nil {
 			return "", err
 		}
 		if hasVariants {
 			pco.po.p.incrPageOutputTemplateVariation()
 		}
-		b, err := pco.renderContentWithConverter(ctx, conv, contentToRender, false)
+		b, err := pco.renderContentWithConverter(ctx, conv, ct.contentToRender, ct.sourceInfo, false)
 		if err != nil {
 			return "", pco.po.p.wrapError(err)
 		}
@@ -998,7 +1017,11 @@ func (c *cachedContentScope) RenderString(ctx context.Context, args ...any) (tem
 		pco.po.p.m.content.hasShortcode.Store(&combined)

 	} else {
-		c, err := pco.renderContentWithConverter(ctx, conv, []byte(contentToRender), false)
+		si := sourceInfo{
+			filename: pco.po.p.pathOrTitle() + " (rendered from string)",
+			source:   []byte(contentToRender),
+		}
+		c, err := pco.renderContentWithConverter(ctx, conv, si.source, si, false)
 		if err != nil {
 			return "", pco.po.p.wrapError(err)
 		}
diff --git a/hugolib/page__per_output.go b/hugolib/page__per_output.go
index 0b889eeb96f..9009165ff2e 100644
--- a/hugolib/page__per_output.go
+++ b/hugolib/page__per_output.go
@@ -89,9 +89,6 @@ type pageContentOutput struct {

 	// Renders Markdown hooks.
 	renderHooks *renderHooks
-
-	// Maps positions in the content sent to Goldmark back to the original source.
-	sourceMap []sourceMapEntry
 }

 func (pco *pageContentOutput) trackDependency(idp identity.IdentityProvider) {
@@ -246,22 +243,25 @@ func (pco *pageContentOutput) initRenderHooks() error {
 		renderCache := make(map[cacheKey]any)
 		var renderCacheMu sync.Mutex

-		resolvePosition := func(_ any, _ []byte, pos int) text.Position {
-			if pos == -1 {
+		resolvePosition := func(renderContext any, pos int) text.Position {
+			rc, ok := renderContext.(converter.RenderContext)
+			var si sourceInfo
+			if ok {
+				si, ok = rc.SourceInfo.(sourceInfo)
+			}
+
+			if pos == -1 || !ok {
 				return text.Position{
 					Filename: pco.po.p.pathOrTitle(),
 				}
 			}
-			sourceOrig := pco.po.p.m.content.mustSource()
-			var offset int
-
-			if sm := pco.sourceMap; len(sm) > 0 {
-				offset = resolveSourceOffset(sm, pos)
-			} else {
-				offset = pos + pco.po.p.m.content.pi.posMainContent
+			offset := resolveSourceOffset(si.sourceMap, pos)
+			filename := si.filename
+			if filename == "" {
+				filename = pco.po.p.pathOrTitle()
 			}

-			return pco.po.p.posFromInput(sourceOrig, offset)
+			return posFromInput(filename, si.source, offset)
 		}

 		pco.renderHooks.getRenderer = func(tp hooks.RendererType, id any) any {
@@ -411,7 +411,10 @@ func (cp *pageContentOutput) ParseAndRenderContent(ctx context.Context, content
 	if err != nil {
 		return nil, err
 	}
-	return cp.renderContentWithConverter(ctx, c, content, renderTOC)
+	si := sourceInfo{
+		source: content,
+	}
+	return cp.renderContentWithConverter(ctx, c, content, si, renderTOC)
 }

 func (pco *pageContentOutput) ParseContent(ctx context.Context, content []byte) (converter.ResultParse, bool, error) {
@@ -433,7 +436,7 @@ func (pco *pageContentOutput) ParseContent(ctx context.Context, content []byte)
 	return r, ok, err
 }

-func (pco *pageContentOutput) RenderContent(ctx context.Context, content []byte, doc any) (converter.ResultRender, bool, error) {
+func (pco *pageContentOutput) RenderContent(ctx context.Context, content []byte, sourceInfo, doc any) (converter.ResultRender, bool, error) {
 	c, err := pco.getContentConverter()
 	if err != nil {
 		return nil, false, err
@@ -445,6 +448,7 @@ func (pco *pageContentOutput) RenderContent(ctx context.Context, content []byte
 	rctx := converter.RenderContext{
 		Ctx:         ctx,
 		Src:         content,
+		SourceInfo:  sourceInfo,
 		RenderTOC:   true,
 		GetRenderer: pco.renderHooks.getRenderer,
 	}
@@ -452,11 +456,12 @@ func (pco *pageContentOutput) RenderContent(ctx context.Context, content []byte,
 	return r, ok, err
 }

-func (pco *pageContentOutput) renderContentWithConverter(ctx context.Context, c converter.Converter, content []byte, renderTOC bool) (converter.ResultRender, error) {
+func (pco *pageContentOutput) renderContentWithConverter(ctx context.Context, c converter.Converter, content []byte, sourceInfo any, renderTOC bool) (converter.ResultRender, error) {
 	r, err := c.Convert(
 		converter.RenderContext{
 			Ctx:         ctx,
 			Src:         content,
+			SourceInfo:  sourceInfo,
 			RenderTOC:   renderTOC,
 			GetRenderer: pco.renderHooks.getRenderer,
 		})
diff --git a/hugolib/shortcode.go b/hugolib/shortcode.go
index c680620cfbe..aae03305117 100644
--- a/hugolib/shortcode.go
+++ b/hugolib/shortcode.go
@@ -553,7 +553,7 @@ func (s *shortcodeParseInfo) prepareShortcodesForPage(po *pageOutput, isRenderSt
 }

 func posFromInput(filename string, input []byte, offset int) text.Position {
-	if offset < 0 {
+	if offset < 0 || offset > len(input) {
 		return text.Position{
 			Filename: filename,
 		}
diff --git a/hugolib/site.go b/hugolib/site.go
index 9c7c51fd1ca..678fea7cddd 100644
--- a/hugolib/site.go
+++ b/hugolib/site.go
@@ -1682,7 +1682,7 @@ var infoOnMissingLayout = map[string]bool{
 type hookRendererTemplate struct {
 	templateHandler *tplimpl.TemplateStore
 	templ           *tplimpl.TemplInfo
-	resolvePosition func(ctx any, srcRender []byte, pos int) text.Position
+	resolvePosition func(renderContext any, pos int) text.Position
 }

 func (hr hookRendererTemplate) RenderLink(cctx context.Context, w io.Writer, ctx hooks.LinkContext) error {
@@ -1709,8 +1709,8 @@ func (hr hookRendererTemplate) RenderTable(cctx context.Context, w hugio.FlexiWr
 	return hr.templateHandler.ExecuteWithContext(cctx, hr.templ, w, ctx)
 }

-func (hr hookRendererTemplate) ResolvePosition(ctx any, srcRender []byte, pos int) text.Position {
-	return hr.resolvePosition(ctx, srcRender, pos)
+func (hr hookRendererTemplate) ResolvePosition(renderContext any, pos int) text.Position {
+	return hr.resolvePosition(renderContext, pos)
 }

 func (hr hookRendererTemplate) IsDefaultCodeBlockRenderer() bool {
diff --git a/markup/converter/converter.go b/markup/converter/converter.go
index 0d5da5e69fc..b4d820bbb77 100644
--- a/markup/converter/converter.go
+++ b/markup/converter/converter.go
@@ -150,6 +150,9 @@ type RenderContext struct {
 	// Src is the content to render.
 	Src []byte

+	// SourceInfo holds optional information about the source of the content to render.
+	SourceInfo any
+
 	// Whether to render TableOfContents.
 	RenderTOC bool

 diff --git a/markup/converter/hooks/hooks.go b/markup/converter/hooks/hooks.go
index 411d16f0bf4..d64998e8500 100644
--- a/markup/converter/hooks/hooks.go
+++ b/markup/converter/hooks/hooks.go
@@ -200,11 +200,8 @@ type HeadingRenderer interface {
 // This may be both slow and approximate, so should only be
 // used for error logging.
 type ElementPositionResolver interface {
-	// ResolvePosition returns the position of the element in the original source document.
-	// ctx is the context passed to the render hook, and srcPos is the zero-based byte offset of the element
-	// in srcRender (the rendered source buffer),
-	// -1 if it's not defined.
-	ResolvePosition(ctx any, srcRender []byte, srcPos int) text.Position
+	// ResolvePosition returns the position of the element in the original source document, -1 if it's not defined.
+	ResolvePosition(renderContext any, srcPos int) text.Position
 }

 type RendererType int
diff --git a/markup/goldmark/internal/render/context.go b/markup/goldmark/internal/render/context.go
index e95d44bbaa6..7daf1c07161 100644
--- a/markup/goldmark/internal/render/context.go
+++ b/markup/goldmark/internal/render/context.go
@@ -184,7 +184,7 @@ func NewBaseContext(rctx *Context, renderer any, n ast.Node, src []byte, ordina

 	b.createPos = func() htext.Position {
 		if resolver, ok := renderer.(hooks.ElementPositionResolver); ok {
-			return resolver.ResolvePosition(b, src, n.Pos())
+			return resolver.ResolvePosition(rctx.RenderContext(), n.Pos())
 		}

 		return htext.Position{
diff --git a/resources/page/page.go b/resources/page/page.go
index 0f5af33e3e3..cc7b96448ef 100644
--- a/resources/page/page.go
+++ b/resources/page/page.go
@@ -114,7 +114,7 @@ type ContentRenderer interface {
 	// For internal use only.
 	ParseContent(ctx context.Context, content []byte) (converter.ResultParse, bool, error)
 	// For internal use only.
-	RenderContent(ctx context.Context, content []byte, doc any) (converter.ResultRender, bool, error)
+	RenderContent(ctx context.Context, content []byte, sourceInfo, doc any) (converter.ResultRender, bool, error)
 }

 // FileProvider provides the source file.
diff --git a/resources/page/page_lazy_contentprovider.go b/resources/page/page_lazy_contentprovider.go
index 78ca09bbed1..84fb246826f 100644
--- a/resources/page/page_lazy_contentprovider.go
+++ b/resources/page/page_lazy_contentprovider.go
@@ -133,6 +133,6 @@ func (lcp *LazyContentProvider) ParseContent(ctx context.Context, content []byte)
 	return lcp.init.Value(ctx).ParseContent(ctx, content)
 }

-func (lcp *LazyContentProvider) RenderContent(ctx context.Context, content []byte, doc any) (converter.ResultRender, bool, error) {
-	return lcp.init.Value(ctx).RenderContent(ctx, content, doc)
+func (lcp *LazyContentProvider) RenderContent(ctx context.Context, content []byte, sourceInfo, doc any) (converter.ResultRender, bool, error) {
+	return lcp.init.Value(ctx).RenderContent(ctx, content, sourceInfo, doc)
 }
diff --git a/resources/page/page_nop.go b/resources/page/page_nop.go
index 80fe5025829..900857902da 100644
--- a/resources/page/page_nop.go
+++ b/resources/page/page_nop.go
@@ -522,7 +522,7 @@ func (r *nopContentRenderer) ParseContent(ctx context.Context, content []byte)
 	return nil, false, nil
 }

-func (r *nopContentRenderer) RenderContent(ctx context.Context, content []byte, doc any) (converter.ResultRender, bool, error) {
+func (r *nopContentRenderer) RenderContent(ctx context.Context, content []byte, sourceInfo, doc any) (converter.ResultRender, bool, error) {
 	return nil, false, nil
 }

diff --git a/tpl/tplimpl/render_hook_integration_test.go b/tpl/tplimpl/render_hook_integration_test.go
index 0c7d85591a4..ea1c33239a7 100644
--- a/tpl/tplimpl/render_hook_integration_test.go
+++ b/tpl/tplimpl/render_hook_integration_test.go
@@ -466,3 +466,44 @@ This is an \\(inline\\) passthrough element with opening and closing inline delimi
 		"passthrough.passthroughContext|p1.md|46:12|2|",
 	)
 }
+
+func TestRenderHooksPositionRenderString(t *testing.T) {
+	t.Parallel()
+
+	files := `
+-- hugo.toml --
+-- assets/a.txt --
+
+## Heading
+
+[link](b.txt)
+
+-- assets/b.txt --
+{{% myshortcode %}}
+{{< myshortcode >}}
+
+
+
+  [link](a.txt)
+-- layouts/shortcodes/myshortcode.html --
+My Shortcode.
+# This is a heading in the shortcode.
+Some text.
+-- layouts/_markup/render-link.html --
+{{ $pos := .Position }}
+{{ printf "%T" . }}|{{ path.Join $pos.Filename }}|{{ printf "%d:%d" $pos.LineNumber $pos.ColumnNumber }}|{{ $.Ordinal }}|
+-- layouts/all.html --
+{{ $a := resources.Get "a.txt" }}
+a: {{ .RenderString $a.Content }}
b: {{ .RenderString (resources.Get "b.txt").Content }}
+-- content/p1.md --
+
+
+`
+
+	b := hugolib.Test(t, files)
+	b.AssertFileContent("public/p1/index.html",
+		"/content/p1.md (rendered from string)|4:1|0|",
+		"/content/p1.md (rendered from string)|6:3|0|",
+	)
+}
PATCH

echo "Patch applied successfully!"
