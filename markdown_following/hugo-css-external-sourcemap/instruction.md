# Fix External Source Maps in Hugo's CSS Build

## Problem

When building CSS with external source maps enabled, Hugo's esbuild integration is not correctly preserving source file paths in the generated source maps. This causes browser developer tools to fail to map minified CSS back to its original source files.

## Symptoms

- External source maps for CSS builds have missing or incorrect source paths
- Browser dev tools cannot resolve original CSS file locations
- Sources listed in the source map are empty or point to non-existent paths

## Affected Areas

The bug spans two internal modules and two test files:

1. **Source map processing** — The code that filters and processes source map entries uses a separate helper function that resolves sources but does not properly align source content metadata alongside the sources. The source content tracking and source filtering need to happen together.

2. **Build client source resolution** — The resolve callback inside the build client treats all non-namespace source paths the same way, returning empty strings for source files that should be kept. A distinction between output files (which live in the publish directory) and source files (which live in the assets tree) is missing.

3. **CSS build integration tests** — These tests check source map content but do not validate the full source list. They also only test with a single minification setting.

4. **JS build integration tests** — The source count expectation in the JS source map test does not match the actual number of source files produced.

## Expected Behavior

After the fix:
- CSS builds with `sourceMap: "external"` should generate source maps with all 4 CSS sources listed (main.css + foo.css + bar.css + baz.css)
- Source file paths should be properly resolved to absolute filenames and converted to URLs
- Both minified and unminified CSS builds should work correctly with source maps
- The JS integration test should expect 5 sources in its source map (was 4)

## Testing

The repository has existing tests that validate this behavior:
- Run `go test -v -run TestCSSBuild ./tpl/css/` to test CSS builds
- Run `go test -v ./internal/js/esbuild/...` to test source map functionality
- Run `go test -v -run TestBuildJS ./resources/resource_transformers/js/...` to test JS builds

The tests should pass after your fix and fail without it.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt` (Go formatter)
