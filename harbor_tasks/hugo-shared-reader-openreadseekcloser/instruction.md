# Fix shared reader in Source.ValueAsOpenReadSeekCloser

## Problem

When using `AddResource` with content from `resources.Get` in a `_content.gotmpl` template, Hugo panics or produces corrupted output during image processing (e.g., `.Resize`). The issue occurs because `Source.ValueAsOpenReadSeekCloser()` returns an opener that shares a single underlying reader across all calls. When the opener is called multiple times (as Hugo does internally during resource processing), the readers interfere with each other — opening a second reader resets the read position of the first, causing data corruption.

For example, a template like this will fail:

```
{{ $pixel := resources.Get "a/pixel.png" }}
{{ $content := dict "mediaType" $pixel.MediaType.Type "value" $pixel.Content }}
{{ $.AddPage (dict "path" "p1" "title" "p1") }}
{{ $.AddResource (dict "path" "p1/pixel.png" "content" $content) }}
```

When the page template tries to `.Resize` the added resource, the operation fails because the shared reader state is corrupted by concurrent opens.

## Expected Behavior

Each call to the opener returned by `ValueAsOpenReadSeekCloser()` should return a completely independent reader with its own position. Multiple readers should be able to coexist without interfering with each other.

## Files to Look At

- `resources/page/pagemeta/page_frontmatter.go` — contains the `Source` type and its `ValueAsOpenReadSeekCloser()` method
