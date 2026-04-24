# Fix Phantom Taxonomy Bug in Hugo

## Problem

When non-taxonomy configuration keys (e.g., `disableKinds = []`) are placed after the `[taxonomies]` section in a Hugo site's TOML config file, they become part of the taxonomies table due to TOML's table syntax. An entry with an empty value creates a "phantom taxonomy" with an empty `pluralTreeKey`, which causes the `.Ancestors` template function to loop indefinitely.

## Example of problematic config

```toml
baseURL = "http://example.com/"
title = "My Site"
[taxonomies]
  tag = "tags"
disableKinds = []  # This becomes part of [taxonomies] due to TOML parsing!
```

In this case, `disableKinds` becomes a taxonomy entry with an empty value (or `disableKinds` = `[]` becomes a key with empty value after type conversion). When Hugo tries to walk `.Ancestors` for a page, it encounters this phantom taxonomy and enters an infinite loop.

## Reproduction

1. Create a Hugo site with the problematic config structure shown above
2. Create a page with tags: `tags: [demo]` in front matter
3. In a template, access `.Ancestors` (e.g., `{{ range .Ancestors }}{{ .Title }}{{ end }}`)
4. Hugo will hang indefinitely

## Your Task

Find and fix the bug in Hugo's taxonomy configuration parsing. The fix should:

1. Filter out taxonomy entries that have empty keys or empty values
2. Handle the edge case where malformed config entries slip through
3. Not break any existing functionality

## Hints

- The issue is in the config parsing/decoding layer
- Look for where taxonomies are loaded from config
- The fix should be defensive - filter out invalid entries rather than trying to fix the TOML parser
- Hugo uses a custom config decoder system in `config/allconfig/`
- The test file `hugolib/disableKinds_test.go` contains a test case `TestDisableKindsEmptySliceAncestors` that reproduces this issue

## Files Likely Involved

- `config/allconfig/alldecoders.go` - Contains the taxonomy config decoder
- `hugolib/disableKinds_test.go` - Contains the reproduction test case

## Expected Behavior

After the fix:
- Empty taxonomy keys should be filtered out during config parsing
- Empty taxonomy values should be filtered out during config parsing
- `.Ancestors` should work correctly even with malformed config
- The existing test `TestDisableKindsEmptySliceAncestors` should pass

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
