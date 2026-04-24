# Fix SVG Minification to Preserve Alpine.js Directives

## Problem

The SVG minifier in Hugo is stripping Alpine.js directives from SVG content. Specifically:

- `x-bind:href` attributes are being removed from SVG elements
- The shorthand `:href` syntax is also being stripped

This breaks Alpine.js functionality when used within SVG elements, which is commonly needed for dynamic icon systems.

## Example

The following SVG content:
```html
<use x-bind:href="myicon">
<use :href="myicon">
```

Is being minified incorrectly, removing the Alpine.js directives.

## Expected Behavior

After minification, Alpine.js directives must be preserved:
- `x-bind:href="myicon"` must remain in the output
- `:href="myicon"` must remain in the output

## Requirements

1. **Dependency Update**: Update the `tdewolff/minify` dependency in `go.mod` to version `v2.24.11`. This version contains the namespace preservation features needed to fix this issue.

2. **SVG Minifier Configuration**: The Hugo minifier uses the `tdewolff/minify` library. Configure the SVG minifier's `KeepNamespaces` option with the value `[]string{"", "x-bind"}`. This preserves both the default namespace (for shorthand `:href`) and the `x-bind` namespace.

3. **Regression Tests**: Add test cases in `minifiers/minifiers_test.go` that verify Alpine.js directives are preserved. The tests must:
   - Reference issue "#14669" in a comment
   - Include a test case with `x-bind:href="myicon"`
   - Include a test case with `:href="myicon"`

4. **Existing Tests**: All existing tests must continue to pass (`go test ./minifiers/...`, `go build ./`, `go vet ./minifiers/...`).

## Related Issue

This fixes issue #14669 where Alpine.js directives in SVGs were being stripped by the minifier.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
