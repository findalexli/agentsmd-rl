# Fix Deprecated Hugo Tokens in Test Files

## Problem

Several test files in the Hugo repository are using deprecated tokens and APIs that cause test failures or deprecation warnings:

1. **Permalink tokens**: The `:filename` token in permalink configurations has been deprecated and replaced with `:contentbasename`. Similarly, `:slugorfilename` has been replaced with `:slugorcontentbasename`.

2. **Data access**: The `.Site.Data` template function has been deprecated and replaced with `hugo.Data`.

These deprecated tokens cause the Go tests to fail with deprecation errors.

## Affected Files

The following test files need to be updated:

- `hugolib/hugo_sites_multihost_test.go` - Uses `:filename` in permalink config
- `hugolib/page_test.go` - Uses `:filename` in permalink config
- `hugolib/pagebundler_test.go` - Uses `:slugorfilename` in permalink config
- `hugolib/hugo_modules_test.go` - Uses `.Site.Data` in template
- `resources/page/permalinks_integration_test.go` - Uses `:filename` in multiple places

## Your Task

Update all deprecated tokens in these test files to use their modern equivalents:
- Replace `:filename` with `:contentbasename`
- Replace `:slugorfilename` with `:slugorcontentbasename`
- Replace `.Site.Data` with `hugo.Data`

You may also need to update expected output paths in test assertions that depend on these permalink configurations.

## How to Test

After making changes, run the affected Go tests:

```bash
cd /workspace/hugo

# Test permalink functionality
go test -run TestPermalinks ./resources/page/...

# Test multihost functionality
go test -run TestMultiHost ./hugolib/...

# Test page bundler
go test -run TestHTMLFilesIsue11999 ./hugolib/...

# Test hugo modules data access
go test -run TestMount ./hugolib/...

# Test page paths
go test -run TestPagePathDisablePathToLower ./hugolib/...
```

All tests should pass without deprecation errors.

## Hints

- Search for the deprecated tokens (`:filename`, `:slugorfilename`, `.Site.Data`) to find all occurrences
- Look for expected file paths in test assertions that might need updating when permalink tokens change
- The Hugo project uses `qt` matchers for test assertions - maintain this style if you need to modify assertions
- Run `./check.sh ./path/to/package/...` when iterating on changes
