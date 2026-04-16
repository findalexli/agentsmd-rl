# Fix Double-Escaping of Ampersands in Link URLs

## Problem

When rendering markdown links that contain query parameters with ampersands (e.g., `https://a.com/?a=1&b=2`), the ampersands are being incorrectly double-escaped, resulting in `&amp;amp;` instead of the correct `&amp;` in the output HTML.

## Expected Behavior

A markdown link like:
```markdown
[foo](https://a.com/?a=1&b=2)
```

Should render to:
```html
<a href="https://a.com/?a=1&amp;b=2">foo</a>
```

## Actual Behavior

The link renders to:
```html
<a href="https://a.com/?a=1&amp;amp;b=2">foo</a>
```

The `&b=2` portion is being double-escaped to `&amp;amp;b=2` instead of the correct single-escape `&amp;b=2`. This suggests the HTML escaping is being applied twice to the link destination.

## Verification

The fix is verified by running the integration test `TestRenderLinkDefaultAmpersand` in `markup/goldmark/goldmark_integration_test.go`:

```bash
go test -v -run TestRenderLinkDefaultAmpersand ./markup/goldmark/...
```

This test renders a markdown link containing a URL with query parameters including an ampersand (`[foo](https://a.com/?a=1&b=2)`) and asserts that the output HTML contains `&amp;b=2` (not `&amp;amp;b=2`).

A complementary test in `markup/goldmark/render_hooks.go` verifies the link rendering logic produces correctly-escaped HTML.

Also run the full goldmark test suite to ensure no regressions:

```bash
go test -v ./markup/goldmark/...
```
