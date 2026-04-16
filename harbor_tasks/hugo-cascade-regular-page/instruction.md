# Hugo Cascade to Self Bug Fix

## Problem Description

Regular pages (leaf bundles and single pages) in Hugo cannot currently apply cascade frontmatter to themselves. Cascade frontmatter allows setting build options (like `render: never`, `list: never`) that cascade to descendant pages. However, the current implementation only processes cascade frontmatter for branch nodes (sections, home page), not for regular pages.

When a regular page has cascade frontmatter targeting the current environment, those build options should apply to the page itself. Currently, this doesn't work - the cascade is silently ignored for regular pages.

## Example

Given this site structure:

```
content/
  s1/
    _index.md     # Section with cascade frontmatter
    p1.md         # Regular page (inherits cascade from section)
  s2/
    _index.md     # Section without cascade
    p2.md         # Regular page with cascade frontmatter
    p3/
      index.md    # Leaf bundle with cascade frontmatter
```

With `p2.md` containing:
```yaml
---
title: p2
cascade:
  target:
    environment: pubweb
  build:
    render: never
---
```

And `hugo.toml` setting `environment = 'pubweb'`, the page `p2` should NOT be rendered to `public/s2/p2/index.html` because the cascade `render: never` should apply to itself.

Similarly, for a leaf bundle `p3/index.md` with the same cascade frontmatter, it should NOT render to `public/s2/p3/index.html`.

Section `s1` with cascade frontmatter targeting the current environment should also NOT be rendered to `public/s1/index.html` (cascade applies to self for sections too).

Currently, these cascades are ignored for regular pages and they are rendered anyway.

## Expected Behavior

After the fix:
- Regular pages (leaf bundles like `p3/index.md` and single pages like `p2.md`) with cascade frontmatter targeting the current environment should NOT render their output files
- Specifically, with `environment = 'pubweb'`:
  - `public/s2/p2/index.html` should NOT exist
  - `public/s2/p3/index.html` should NOT exist
- Section `s1` with cascade targeting the environment should NOT render `public/s1/index.html`
- Section `s2` without cascade should render `public/s2/index.html` normally
- The `target.environment` matching should work for regular pages with environment values including: `prod`, `staging`, `dev`, `testing`, and custom environment names
- All existing cascade tests should continue to pass

## Testing

Run tests in the `hugolib` package to verify:
```bash
go test -run TestCascade ./hugolib/
go test ./hugolib/
```