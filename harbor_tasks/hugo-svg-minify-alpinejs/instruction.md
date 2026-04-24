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

The underlying minification is done by the `github.com/tdewolff/minify/v2` library. A recent version of this library added support for preserving custom XML namespaces in SVG via a new configuration option. This option allows specifying a list of namespace prefix strings to keep during minification.

The Hugo project uses this library for SVG minification in the `minifiers/` package. You will need to:
1. Update the `github.com/tdewolff/minify/v2` dependency to a version that includes namespace preservation support
2. Configure the SVG minifier in Hugo to preserve the namespaces used by Alpine.js directives

## Verification

After implementing the fix, verify:
1. `<use x-bind:href="icon">` minifies unchanged (input equals output)
2. `<use :href="icon">` minifies unchanged (input equals output)
3. `<circle x-bind:r="radius">` minifies unchanged (input equals output)
4. `<circle :cx="x">` minifies unchanged (input equals output)
5. The Hugo project compiles successfully
6. All existing minifier tests continue to pass

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
