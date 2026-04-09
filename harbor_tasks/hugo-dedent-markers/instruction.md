# Fix RenderShortcodes leaking context markers when indented

## Problem

When a Hugo shortcode includes `RenderShortcodes` and the template code is indented (e.g., inside a nested block), Hugo's internal context markers are being treated as indented code blocks by the Goldmark markdown parser. This causes the markers to leak into the rendered output.

The context markers (like `{{__hugo_ctx pid=123}}`) are internal tracking tokens that should never appear in the final rendered HTML.

## Files to Investigate

1. `markup/goldmark/hugocontext/hugocontext.go` - This package handles the context markers
2. `hugolib/page__content.go` - The content rendering pipeline where the fix should be integrated

## Expected Behavior

Context markers should be stripped of their leading whitespace before markdown parsing occurs, preventing Goldmark from treating them as code blocks. The markers should still function correctly for internal tracking but not appear in output.

## Reproduction Scenario

Consider a setup where:
- A shortcode template is indented (e.g., 4 spaces inside a conditional)
- The template calls `{{ $p.RenderShortcodes }}`
- The included page has simple markdown content

Without the fix, the rendered output will contain visible Hugo context markers that should have been stripped.

## Implementation Notes

- The fix should handle both spaces and tabs as leading whitespace
- The fix should not affect content that doesn't contain context markers
- Look at how the `Strip` function works for inspiration
- The fix needs to be applied before Goldmark parsing
