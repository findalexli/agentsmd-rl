# Hugo Convert: Preserve Non-Content Files in Output

## Problem

When running `hugo convert` with the `--output` (or `-o`) flag to convert front matter formats, non-content files in page bundles are **not** copied to the output directory. This causes data loss for sites that rely on page bundles containing resources like images, data files, or other assets.

## Example

A page bundle with this structure:

```
content/
└── bundle/
    ├── index.md       # Content file (gets converted)
    ├── data.txt       # Resource file (LOST - not copied!)
    └── nested/
        └── asset.dat  # Nested resource (LOST - not copied!)
```

After running `hugo convert toJSON -o outputdir/`, only `index.md` appears in the output. The `data.txt` and `nested/asset.dat` files are missing.

## Expected Behavior

All non-content files in the content tree should be preserved in the output directory, alongside the converted content files.

## Relevant Files

- `commands/convert.go` - Contains the convert command implementation
  - `convertContents()` - Main conversion function
  - `convertAndSavePage()` - Converts and saves individual pages

## Hints

- The fix should copy the content directory tree to the output location **before** converting content files
- To avoid infinite recursion when the output path is inside the content tree, you'll need to skip the output directories during copy
- Hugo has helper functions for file operations - look in `common/hugio` for `CopyDir`
- The `hugofs.Os` filesystem abstraction is available for file operations

## Testing

Your fix should:
1. Compile successfully: `go build -o hugo .`
2. Pass the existing tests: `go test ./commands/...`
3. Preserve bundle resources when running `hugo convert toJSON -o <dir>`

## References

- Original issue: https://github.com/gohugoio/hugo/issues/4621
