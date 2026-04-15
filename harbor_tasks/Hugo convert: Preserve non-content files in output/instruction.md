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

All non-content files in the content tree should be preserved in the output directory, alongside the converted content files. This must work for all three conversion formats: `toJSON`, `toTOML`, and `toYAML`.

## Testing

Your fix should:
1. Compile successfully: `go build -o hugo .`
2. Pass the existing tests: `go test ./commands/...`
3. Preserve bundle resources when running `hugo convert toJSON -o <dir>`
4. Work with all conversion formats (toJSON, toTOML, toYAML)

## References

- Original issue: https://github.com/gohugoio/hugo/issues/4621
