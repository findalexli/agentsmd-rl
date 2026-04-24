# Fix External Source Maps in Hugo's CSS Build

## Problem

When building CSS with external source maps enabled, Hugo's esbuild integration is not correctly preserving source file paths in the generated source maps. This causes browser developer tools to fail to map minified CSS back to its original source files.

## Symptoms

- External source maps for CSS builds have missing or incorrect source paths
- Browser dev tools cannot resolve original CSS file locations
- Sources listed in the source map are empty or point to non-existent paths

## Affected Files

The fix involves changes to these files:

1. **internal/js/esbuild/sourcemap.go** - The core source map processing logic
   - Currently uses a separate `fixSourceMapSources()` function that filters sources
   - Needs to handle source content alignment properly

2. **internal/js/esbuild/build.go** - The esbuild client build logic
   - Source file resolution function returns empty string for source files
   - Should return the absolute filename for valid source files

3. **tpl/css/build_integration_test.go** - CSS build tests
   - Needs to validate source counts and test both minified/unminified builds

4. **resources/resource_transformers/js/js_integration_test.go** - JS build tests
   - Source count expectation needs adjustment

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

The tests should pass after your fix and fail without it.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
