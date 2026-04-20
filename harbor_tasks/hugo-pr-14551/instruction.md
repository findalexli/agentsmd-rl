# Hugo Taxonomy Empty Key Fix

## Symptom

When a Hugo site's TOML configuration has non-taxonomy keys placed after the `[taxonomies]` section, those keys incorrectly become entries in the taxonomies map. For example:

```toml
[taxonomies]
  tag = "tags"
disableKinds = []
```

The `disableKinds = []` entry (with an empty value) becomes a phantom taxonomy entry with an empty key. When a page has taxonomy terms (e.g. `tags: [demo]`), calling `.Ancestors` on that page either:
- Produces an incorrect ancestor count, or
- Causes the page build to hang indefinitely

## Expected Behavior

Taxonomy entries with empty keys or empty values must be filtered out. Pages with taxonomy terms should render correctly with `.Ancestors` returning the expected count (exactly 2 ancestors: `section` and `home`).

## Files Affected

The taxonomy decoder in `config/allconfig/alldecoders.go` handles parsing of the `[taxonomies]` section in TOML config files. This is where the fix must be applied.

## Verification

Build Hugo and create a test site with the configuration above. Render a page that uses `.Ancestors`. The output should show exactly 2 ancestors (`section|home`) without hanging.

```bash
go build
./hugo --source=/path/to/test/site
```

Then check the rendered page for the correct ancestor count.
