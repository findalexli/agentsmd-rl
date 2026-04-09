# Fix Phantom Taxonomy Bug in Hugo Configuration

## Problem

When non-taxonomy configuration keys (like `disableKinds = []`) are placed after the `[taxonomies]` section in Hugo's TOML config file, they become part of the taxonomies table. An empty-valued entry creates a phantom taxonomy with an empty `pluralTreeKey`, which causes `.Ancestors` to loop indefinitely when rendering pages.

This was reported in issue #14550.

## Example Bug Trigger

```toml
# hugo.toml
baseURL = "http://example.com/"
title = "Bug repro"

[taxonomies]
  tag = "tags"
disableKinds = []  # This becomes part of taxonomies table!
```

The `disableKinds = []` line, when placed after `[taxonomies]` in TOML, is interpreted as being inside the taxonomies table. This creates a phantom taxonomy entry with an empty key or value, which then causes the `.Ancestors` template function to hang indefinitely.

## Your Task

Fix the taxonomy configuration decoder to skip entries with empty keys or values. The fix should:

1. Filter out invalid taxonomy entries (those with empty keys or values) when parsing the taxonomies configuration
2. Prevent the creation of phantom taxonomies that cause `.Ancestors` to loop
3. Ensure valid taxonomies (like `tag = "tags"`) continue to work normally

## Relevant Files

- `config/allconfig/alldecoders.go` - Contains the taxonomy configuration decoder
- `hugolib/disableKinds_test.go` - Contains the existing test that reproduces the issue

## Hints

- Look for the "taxonomies" decoder in `alldecoders.go`
- The fix should be applied after the config string map is cleaned but before it's assigned
- The test `TestDisableKindsEmptySliceAncestors` in `disableKinds_test.go` shows the expected behavior

## Expected Behavior

After the fix:
- Pages should render without hanging when `.Ancestors` is called
- Taxonomy entries with empty keys or values should be silently ignored
- Valid taxonomy configurations should continue to work as expected
