# Hugo SVG Minification Bug

## Problem

Hugo's SVG minifier is incorrectly stripping Alpine.js directives from SVG elements. This breaks interactive components that use Alpine.js for dynamic SVG attributes.

## Symptoms

When minifying SVG content that contains Alpine.js directives:
- `x-bind:href="myicon"` gets stripped or modified
- `:href="myicon"` (the shorthand) gets stripped or modified

This causes Alpine.js applications to break because the dynamic bindings are removed during the minification process.

## Files to Examine

- `minifiers/config.go` - The minifier configuration
- `minifiers/minifiers_test.go` - Existing tests for reference

## Expected Behavior

Alpine.js directives should be preserved in SVG minification:
- The `x-bind` namespace should be kept
- The empty namespace (for shorthand like `:href`) should be kept

## Context

This issue affects users who use Alpine.js with SVG elements. The underlying minification is done by `tdewolff/minify` library, which recently added support for preserving specific namespaces via a `KeepNamespaces` configuration option.

The fix involves:
1. Updating the `tdewolff/minify` dependency to a version that supports `KeepNamespaces`
2. Configuring the SVG minifier to keep both `""` (empty namespace for shorthand) and `"x-bind"` namespaces

## Relevant Code

Look at how the SVG minifier is configured in `minifiers/config.go`. The `defaultTdewolffConfig` struct contains the SVG minifier settings. Compare with how the HTML minifier handles similar attribute preservation.

## Testing

You can verify the fix works by:
1. Creating a test that minifies `<use x-bind:href="myicon">` and verifies it remains unchanged
2. Creating a test that minifies `<use :href="myicon">` and verifies it remains unchanged

Both should pass through minification without modification.
