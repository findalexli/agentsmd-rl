# Fix Deprecated Hugo Tokens in Test Files

## Problem

Several test files in the Hugo repository are using deprecated tokens and APIs. When running the test suite, these deprecated usages cause deprecation errors and test failures.

You can observe these failures by running the Go tests - they will emit deprecation warnings or fail outright when encountering the deprecated patterns.

## Affected Files and Tests

The following test files contain deprecated tokens that need to be identified and updated:

- `hugolib/hugo_sites_multihost_test.go` - permalink configuration
- `hugolib/page_test.go` - permalink configuration
- `hugolib/pagebundler_test.go` - permalink configuration
- `hugolib/hugo_modules_test.go` - template data access
- `resources/page/permalinks_integration_test.go` - permalink configuration

## Verification Requirements

After fixing, the following must be true:

### Permalink Tokens
- Files must use `:contentbasename` instead of the deprecated `:filename` token
- Files must use `:slugorcontentbasename` instead of the deprecated `:slugorfilename` token
- The permalink configuration maps should reflect these updated tokens

### Template Data Access
- Templates must use `hugo.Data` instead of the deprecated `.Site.Data` pattern

### Expected File Paths
Some tests verify specific URL paths are generated. The correct URL paths that should be produced include:
- `public/sectionwithfilefilename/withfilefilename/index.html`
- `public/sectionnofilefilename/nofilefilename/index.html`

## How to Test

After making changes, verify the deprecated patterns have been removed by running the affected Go tests:

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

Tests should pass without deprecation errors.

## Hints

- Search for deprecated tokens in the affected files to understand what needs changing
- The deprecated tokens in these test files are related to filename handling and site data access
- Look for expected file paths in test assertions that may need updating when permalink configurations change
- Run `./check.sh ./path/to/package/...` when iterating on changes

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
