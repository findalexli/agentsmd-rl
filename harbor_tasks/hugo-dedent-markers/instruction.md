# Fix RenderShortcodes leaking context markers when indented

## Problem

When a Hugo shortcode includes `RenderShortcodes` and the template code is indented (e.g., inside a nested block), Hugo's internal context markers are being treated as indented code blocks by the Goldmark markdown parser. This causes the markers to leak into the rendered output.

The context markers follow the pattern `{{__hugo_ctx ...}}` (e.g., `{{__hugo_ctx pid=123}}`, `{{__hugo_ctx end}}`, `{{__hugo_ctx /}}`). These are internal tracking tokens that should never appear in the final rendered HTML.

## Acceptance Criteria

The test suite verifies the following requirements. All must pass:

### DedentMarkers function

The test suite expects an exported function called `DedentMarkers` in the `markup/goldmark/hugocontext` package with signature `func([]byte) []byte`. It must exhibit the following behavior:

- **Strips leading spaces from marker lines:** `"    {{__hugo_ctx pid=123}}"` → `"{{__hugo_ctx pid=123}}"` and `"  {{__hugo_ctx}}"` → `"{{__hugo_ctx}}"`
- **Strips leading tabs from marker lines:** `"\t\t{{__hugo_ctx end}}"` → `"{{__hugo_ctx end}}"`
- **Preserves lines without markers unchanged:** `"regular text without markers"` and `"    indented code block"` are returned as-is
- **Handles multiple markers in one input:** e.g. a multi-line string with `{{__hugo_ctx pid=1}}` and `{{__hugo_ctx /}}` on separate indented lines — only the marker-containing lines should have their leading whitespace removed

### Integration in the content pipeline

The test suite checks that `DedentMarkers` is called from within the `contentToC` function in `hugolib/page__content.go`, ensuring markers are dedented before Goldmark parsing occurs.

### Test helper

The test suite verifies that a method called `AssertNoRenderShortcodesArtifacts` exists somewhere in the Go source tree, for asserting that rendered output is free of shortcode artifacts.

### Integration test

The test `TestRenderShortcodesCodeBlock` in the `hugolib` package must pass. This test validates that `RenderShortcodes` does not leak context markers when the shortcode template is indented.

## Constraints

- All existing tests in the `hugocontext` and `hugolib` packages must continue to pass
- The code must pass `go vet` and be properly formatted (`gofmt`)
