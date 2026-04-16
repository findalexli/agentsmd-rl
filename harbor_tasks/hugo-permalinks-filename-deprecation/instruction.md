# Fix Deprecated Hugo Permalink Tokens

Hugo's integration tests are failing due to deprecated permalink tokens that cause deprecation errors. Your task is to identify and fix these deprecation issues so the tests pass.

## Symptoms

When running the following tests, you will see deprecation errors like these patterns in the output:
- `:filename" permalink token was deprecated`
- `:slugorfilename" permalink token was deprecated`
- `ERROR deprecated`

The affected tests that show these errors are:
- `TestPermalinks` in `resources/page/permalinks_integration_test.go`
- `TestPermalinksNestedSections` in `resources/page/permalinks_integration_test.go`
- `TestPagePathDisablePathToLower` in `hugolib/page_test.go`
- `TestMultiHost` in `hugolib/hugo_sites_multihost_test.go`
- `TestHTMLFilesIsue11999` in `hugolib/pagebundler_test.go`

Additionally, `hugolib/hugo_modules_test.go` uses a deprecated data access pattern that produces errors.

## What You Need To Do

1. Examine the test files mentioned above for TOML configuration blocks containing permalink patterns
2. Identify deprecated permalink tokens (look for patterns starting with `:` in the `[permalinks]` sections)
3. Replace deprecated tokens with their current, non-deprecated equivalents
4. Update any test assertions that check expected output paths to match the behavior of the current tokens
5. Update `hugolib/hugo_modules_test.go` to use the current data access pattern instead of the deprecated one
6. Add the `-failfast` flag to the `go test` command in `check.sh`

## Expected Test Paths After Fix

In `resources/page/permalinks_integration_test.go`, after fixing the deprecated tokens, the following assertions should verify these specific paths:
- `public/sectionwithfilefilename/withfilefilename/index.html`
- `public/sectionnofilefilename/nofilefilename/index.html`

## Files to Examine

- `resources/page/permalinks_integration_test.go` - Contains permalink integration tests with section configurations
- `hugolib/page_test.go` - Contains `TestPagePathDisablePathToLower` with permalink configuration
- `hugolib/hugo_sites_multihost_test.go` - Contains `TestMultiHost` with multi-host permalink settings
- `hugolib/pagebundler_test.go` - Contains `TestHTMLFilesIsue11999` with posts permalink pattern
- `hugolib/hugo_modules_test.go` - Contains deprecated data access pattern in template strings
- `check.sh` - Shell script that needs the `-failfast` flag added to `go test`

## Verification

After making changes, run the tests to verify:
1. No deprecation errors containing `:filename" permalink token was deprecated` appear
2. No deprecation errors containing `:slugorfilename" permalink token was deprecated` appear
3. No `ERROR deprecated` messages appear in test output
4. The `check.sh` script contains `go test -failfast`
