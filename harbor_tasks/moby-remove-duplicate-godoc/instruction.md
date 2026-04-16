# Fix Duplicate Package Documentation

The `daemon/volume/local` package has duplicate package-level documentation that causes godoc to display incorrect or conflicting text.

## Problem

When running `go doc daemon/volume/local` or viewing godoc, the package documentation appears multiple times. This duplication comes from documentation comment blocks appearing in more than one source file within the `daemon/volume/local/` directory.

## What You Need To Do

1. **Resolve the duplicate package documentation.** Audit all Go source files in `daemon/volume/local/` and ensure package-level documentation appears in exactly one file. Files that are not the canonical documentation location should not contain `// Package local provides...` style comment blocks.

2. **Enable a godoc linter** in `.golangci.yml` under the `linters.enable` list to catch duplicate package documentation automatically. This linter must not be commented out.

## Verification

After your changes:
- `go build ./daemon/volume/local/...` succeeds
- `go vet ./daemon/volume/local/...` passes
- `go fmt ./daemon/volume/local/...` passes
- `.golangci.yml` is valid YAML with the linter enabled
- Package-level documentation appears in exactly one file in `daemon/volume/local/`
