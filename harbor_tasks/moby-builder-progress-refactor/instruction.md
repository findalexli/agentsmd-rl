# Refactor Duplicated Progress Helper

## Problem

The codebase contains multiple identical copies of a helper function that creates one-off progress tracking callbacks. These duplicate implementations exist across several files in the `daemon/internal/builder-next` package and all handle creating progress tracking with start/completion timestamps in the same way.

## What You Need To Do

1. Read the files in `daemon/internal/builder-next` that contain local progress helper functions
2. Observe how the local progress helper is called at each call site, noting the context variable and progress ID string passed to it
3. Use `go doc github.com/moby/buildkit/util/progress` or read the buildkit progress package source to understand the API of `progress.OneOff`
4. Replace each call to the local helper function with the appropriate `progress.OneOff` call, using the same context variable and progress ID string that was originally passed to the local function
5. Remove the local helper function definitions
6. Add or remove imports as needed to ensure compilation

## Guidance

The buildkit `progress` package provides a `OneOff` function with the same signature as the local helpers. When refactoring, you must preserve the exact same arguments at each call site - the context variable and the progress ID string must remain identical. Study each call site carefully to understand what arguments are being passed.

## Files to Examine

- `daemon/internal/builder-next/adapters/containerimage/pull.go`
- `daemon/internal/builder-next/exporter/mobyexporter/export.go`
- `daemon/internal/builder-next/exporter/mobyexporter/writer.go`
- `daemon/internal/builder-next/worker/worker.go`

## Verification

After refactoring:
- The project compiles successfully
- Go vet passes
- All unit tests pass
- No duplicate progress helper definitions remain in the modified files