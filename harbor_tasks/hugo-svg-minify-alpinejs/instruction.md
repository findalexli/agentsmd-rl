# Hugo SVG Minification Bug

## Problem

Hugo's SVG minifier is incorrectly stripping Alpine.js directives from SVG elements. This breaks interactive components that use Alpine.js for dynamic SVG attributes.

## Symptoms

When minifying SVG content that contains Alpine.js directives, the following inputs are incorrectly modified (the directives get stripped or altered):

- `<use x-bind:href="icon">` - the `x-bind:href` directive gets stripped
- `<use :href="icon">` - the `:href` shorthand gets stripped
- `<circle x-bind:r="radius">` - the `x-bind:r` directive gets stripped
- `<circle :cx="x">` - the `:cx` shorthand gets stripped

The minifier should preserve these attributes unchanged (input should equal output after minification).

## Technical Context

The underlying minification is done by the `github.com/tdewolff/minify/v2` library. Version `v2.24.11` of this library added support for preserving custom XML namespaces in SVG via a new configuration option that accepts a list of namespace strings to keep.

Two namespace values need to be preserved:
- `""` (empty string) - for shorthand directives like `:href`, `:cx`, etc.
- `"x-bind"` - for explicit x-bind directives like `x-bind:href`, `x-bind:r`, etc.

The Hugo project uses this library for SVG minification in the `minifiers/` package. You will need to:
1. Update the `github.com/tdewolff/minify/v2` dependency to version `v2.24.11` or later
2. Configure the SVG minifier in Hugo to keep both `""` and `"x-bind"` namespaces

## Verification

After implementing the fix, verify:
1. `<use x-bind:href="icon">` minifies unchanged (input equals output)
2. `<use :href="icon">` minifies unchanged (input equals output)
3. `<circle x-bind:r="radius">` minifies unchanged (input equals output)
4. `<circle :cx="x">` minifies unchanged (input equals output)
5. The Hugo project compiles successfully
6. All existing minifier tests continue to pass
