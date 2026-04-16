# Issue #13877: Template Selection Should Prefer Earlier Suffixes

## Problem

When multiple templates exist that differ only in their file extension (suffix), and all those extensions are valid suffixes for the same media type, Hugo selects the template based on alphabetical order rather than the order defined in the media type's suffix list.

## Example Scenario

Given a Hugo site with this configuration:

```toml
[mediaTypes.'text/html']
suffixes = ['b','a','d','c']

[outputFormats.html]
mediaType = 'text/html'
```

And these template files:
- `layouts/page.html.a`
- `layouts/page.html.b`
- `layouts/page.html.c`
- `layouts/page.html.d`

Hugo currently selects `page.html.a` (alphabetically first), but it **should** select `page.html.b` (first in the media type's suffix list).

## What You Need To Do

Find the code in Hugo that handles template selection when a template already exists for a given path. Modify it so that when two templates differ only by extension and both extensions are valid suffixes for the same media type, the template whose extension appears earlier in the media type's suffix list is preferred.

## Requirements

Your fix must satisfy all of the following:

1. **Comment**: Include a comment referencing `Issue #13877` near the changed logic explaining why the comparison is being made.

2. **Implementation**: Use the Go standard library's `slices` package (import as `"slices"`) to determine the position of extensions in the media type's suffix list.

3. **Logic**: When comparing two templates for the same path, get the index of each template's extension in the media type's suffix list using `slices.Index(suffixes, ext)`. The template with the smaller index (earlier in the suffix list) should be kept.

4. **Testing**: After your fix, running `go test -v -run TestTemplateSelectionFirstMediaTypeSuffix ./hugolib/` should pass.

5. **Code Quality**: The code should pass `gofmt`, `go vet ./tpl/tplimpl/...`, and all tests in the `tpl/tplimpl` package.
