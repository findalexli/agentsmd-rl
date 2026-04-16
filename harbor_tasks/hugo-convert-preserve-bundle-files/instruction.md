# Fix hugo convert to preserve non-content bundle files

## Problem

The `hugo convert` command converts content files between front matter formats (TOML, YAML, JSON). When using the `--output` flag to specify a destination directory, it only writes the converted content files and does **not** copy non-content files from page bundles.

Page bundles in Hugo are directories with an `index.md` (or similar) content file along with associated resources like images, data files, or other assets. For example:

```
content/
  mybundle/
    index.md      <- content file (gets converted)
    data.txt      <- resource file (should be preserved but isn't)
    nested/
      asset.dat   <- nested resource (should be preserved but isn't)
```

Running `hugo convert toJSON -o outputdir` creates the converted `index.md` in the output but omits `data.txt` and `nested/asset.dat`. Bundle resource files with content like `bundle resource data` or `nested resource data` are simply not present in the output directory.

## Your Task

Fix the Hugo `convert` command so that when `--output` is specified, all non-content files from content directories are also copied to the output destination.

## Acceptance Criteria

1. **Bundle files preserved**: After `hugo convert toJSON -o outputdir`, non-content files must exist in the output. For example, a file `data.txt` containing `bundle resource data` and a nested file `asset.dat` containing `nested resource data` must both appear in the output directory with their contents intact.

2. **Edge case - output inside content tree**: When the output directory is placed inside the content tree, the command must complete without infinite recursion. The test uses the path `content/output` as the output destination. When a bundle contains a file `resource.txt` containing `resource data`, running `hugo convert toJSON -o content/output` must complete and copy `resource.txt` to the output location without hanging or recursing infinitely.

3. **Code quality**: The solution must compile, pass `go vet`, `gofmt`, and `go mod verify`, and the existing repo tests for the convert command must continue to pass.