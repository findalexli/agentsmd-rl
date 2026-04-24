# Fix intermittent content adapter failures in Hugo

## Problem

There's an intermittent bug in Hugo's content adapter system when creating page resources from string content. When using `AddResource` in a content template to add a resource with content from another resource's `.Content` value, image processing operations like `.Resize` fail intermittently with errors like:

```
error calling Resize: failed to resize image: invalid JPEG format: short Huffman data
```

The image is not actually corrupt - the error occurs randomly and may only appear after running `hugo` multiple times.

## Affected Public API

The issue involves the `pagemeta.Source` struct from package `github.com/gohugoio/hugo/resources/page/pagemeta`. This struct has:
- An exported `Value` field that can be assigned a string directly (e.g., `pagemeta.Source{Value: "some content"}`)
- A method `ValueAsOpenReadSeekCloser()` that returns a function which opens a reader when called

## Reproduction

When a content adapter creates a page resource like this:

```gotemplate
{{ $pixel := resources.Get "a/pixel.png" }}
{{ $content := dict "mediaType" $pixel.MediaType.Type "value" $pixel.Content }}
{{ $.AddPage (dict "path" "p1" "title" "p1") }}
{{ $.AddResource (dict "path" "p1/pixel.png" "content" $content) }}
```

And then the template tries to resize the image:

```gotemplate
{{ with .Resources.Get "pixel.png" }}
{{ with .Resize "1x1" }}Resized: {{ .Width }}x{{ .Height }}{{ end }}
{{ end }}
```

The resize operation intermittently fails.

## Symptom

When multiple readers are obtained from `ValueAsOpenReadSeekCloser()` and used concurrently or sequentially, they interfere with each other's state. Specifically:
- Reading from one reader affects the position/state of another reader
- This causes intermittent corruption when the same source content is accessed multiple times
- The underlying content should be readable in full from each reader independently

## Expected Behavior

After fixing, content adapter resources should work reliably for image processing operations without intermittent errors. The Hugo test suite should pass, particularly tests in `resources/page/pagemeta` and `hugolib/pagesfromdata`.

Multiple readers obtained from the same source should:
1. Each provide access to the complete original content
2. Not share position state between them
3. Be fully independent of each other

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
