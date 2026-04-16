# Task: Fix Deprecated Go Parser APIs in Hugo

## Problem

The file `tpl/internal/templatefuncsRegistry.go` in the Hugo repository at `/workspace/hugo` uses deprecated Go standard library APIs:
- `parser.ParseDir` — deprecated since Go 1.25
- `doc.New` — deprecated

These deprecated calls produce deprecation warnings and will be removed in future Go versions. The code must be updated to use current (non-deprecated) Go APIs while maintaining the same functionality.

## Verification Criteria

After your changes, the file `tpl/internal/templatefuncsRegistry.go` will be verified against all of the following checks. Each criterion must pass:

### Deprecated API Removal
1. The deprecated `parser.ParseDir` call must not appear in the file.
2. The deprecated `doc.New` call must not appear in the file.

### New Code Requirements
3. The file must define an unexported helper function for directory parsing.
4. The file must use the current `parser.ParseFile` API (not `parser.ParseDir`) with comment parsing enabled.
5. The file must use `doc.NewFromFiles` instead of `doc.New`.
6. The file must import the `go/ast` package.

### Build and Quality
7. `go build ./tpl/internal/...` must succeed.
8. `go test ./tpl/internal/...` must pass.
9. `go vet ./tpl/internal/...` must pass.
10. `gofmt -l tpl/internal/` must report no unformatted files.
11. `go build ./...` must succeed.

## Context

This is part of Hugo's template function registry that generates documentation for Hugo's template namespaces by parsing Go source files.
