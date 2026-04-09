# Fix Position Reporting in Hugo RenderString and Render Hooks

## Problem

When using `RenderString` to render content with render hooks, the position information reported by the hooks is incorrect. Instead of reporting positions relative to the rendered string content, hooks are reporting positions based on the parent page's content. This makes debugging and error reporting confusing for users.

## Example Scenario

Consider a page that uses `RenderString` to render external content:

```
-- content/p1.md --
---
---
{{ $a := resources.Get "a.txt" }}
a: {{ .RenderString $a.Content }}

-- assets/a.txt --
## Heading

[link](b.txt)
```

When the render hook for the link is invoked, the `.Position` should indicate:
- Filename: something indicating it was rendered from a string
- Line/Column: position within `a.txt`'s content (line 4, column 1 for the link)

But currently it may report incorrect positions based on the parent page content.

## Key Files to Modify

The fix involves changes across several interconnected components:

1. **hugolib/page__content.go** - Core content rendering logic
   - Add `sourceInfo` struct to track source metadata
   - Update `RenderString` to capture and pass source information
   - Modify content rendering to use sourceInfo for position resolution

2. **hugolib/page__per_output.go** - Per-output content handling
   - Remove `sourceMap` field from `pageContentOutput`
   - Update `resolvePosition` function signature and implementation
   - Modify `RenderContent` and `renderContentWithConverter` to accept `sourceInfo`

3. **hugolib/shortcode.go** - Position calculation
   - Fix bounds check in `posFromInput` (handle `offset > len(input)`)

4. **markup/converter/converter.go** - Converter interface
   - Add `SourceInfo` field to `RenderContext` struct

5. **markup/converter/hooks/hooks.go** - Hook interface
   - Update `ElementPositionResolver.ResolvePosition` signature

6. **Supporting files** - Interface implementations
   - `resources/page/page.go` - Update `ContentRenderer.RenderContent` signature
   - `resources/page/page_lazy_contentprovider.go` - Update lazy wrapper
   - `resources/page/page_nop.go` - Update nop implementation
   - `hugolib/site.go` - Update `hookRendererTemplate.resolvePosition` signature
   - `markup/goldmark/internal/render/context.go` - Update position resolver call

## Testing

There's an existing test `TestRenderHooksPositionRenderString` in `tpl/tplimpl/render_hook_integration_test.go` that validates this fix. The test verifies that:
- Render hooks receive correct filename showing `(rendered from string)`
- Line and column numbers are accurate for the rendered content

Run the test with:
```
go test -v -run TestRenderHooksPositionRenderString ./tpl/tplimpl/...
```

## Implementation Notes

The key insight is that position resolution needs context about the source being rendered. The solution:

1. Create a `sourceInfo` struct containing:
   - `filename`: Override for position reporting (e.g., "page.md (rendered from string)")
   - `source`: The original source bytes
   - `sourceMap`: Maps positions in rendered content back to original source

2. Pass `sourceInfo` through the rendering pipeline via `RenderContext.SourceInfo`

3. Update `resolvePosition` to extract sourceInfo from the RenderContext and use it for accurate position calculation

4. Ensure `RenderString` creates appropriate sourceInfo for its content

This approach ensures that positions are always reported relative to the actual source content being rendered, whether it's from a page file or a rendered string.
