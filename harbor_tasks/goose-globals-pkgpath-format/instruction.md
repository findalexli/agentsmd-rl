# Fix Globals Translation Package Identifier Format

## Problem

The goose Go-to-Coq translator currently produces inconsistent package identifiers when translating global variable accesses from external packages.

When translating Go code that accesses a global variable from another package (e.g., `unittest.GlobalX`), the translator generates Coq code using just the package name:

```coq
globals.get #unittest #"GlobalX"%go
```

However, function calls from the same external package use a different format with `pkgPathBase.pkgName`:

```coq
#unittest.unittest
```

This inconsistency causes the generated Coq output to have mismatched package references - global variables use one format while function calls use another.

## Task

Fix the goose translator in `goose.go` so that global variable accesses use the same `pkgPathBase.pkgName` format as function calls.

The translator currently produces `globals.get` calls with package identifiers like `#unittest` when referencing global variables from external packages. These should instead use the format `#unittest.unittest` (basename of package path + package name) to match how function calls are translated.

## Example

Given this Go code in `testdata/examples/externalglobals/externalglobals.go`:

```go
package externalglobals

import "github.com/goose-lang/goose/testdata/examples/unittest"

func f() {
    unittest.GlobalX = 11
}
```

### Current (incorrect) output:
```coq
globals.get #unittest #"GlobalX"%go
```

### Expected (fixed) output:
```coq
globals.get #unittest.unittest #"GlobalX"%go
```

## Testing

Verify your fix by:

1. Running `go build ./...` to ensure the package compiles
2. Running `go vet -composites=false ./...` to check for issues
3. Running `go test -v -run TestExamples/externalglobals ./...` to test the translation

The gold file at `testdata/examples/externalglobals/externalglobals.gold.v` contains the expected output format with `globals.get #unittest.unittest`.

Key verification: After the fix, the generated Coq output for `globals.get` calls should use the format `#unittest.unittest` instead of just `#unittest` when accessing globals from external packages.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
