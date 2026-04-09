# Remove deprecated Int and String types from internal/cri/setutils

The `internal/cri/setutils` package contains deprecated `Int` and `String` set types that should be removed. These were added as copies from "k8s.io/apimachinery/pkg/util/sets" but are now superseded by the generic `Set[T]` type.

## What needs to be fixed

1. **Remove deprecated type files**: The `int.go` and `string.go` files in `internal/cri/setutils/` define deprecated `Int` and `String` set types. These should be removed entirely.

2. **Remove internal helper**: The `cast` function in `internal/cri/setutils/set.go` was used to convert between the deprecated types and the generic Set. It should be removed since it's no longer needed.

3. **Update usage in util/strings.go**: The `MergeStringSlices` function in `internal/cri/util/strings.go` currently uses the deprecated `setutils.NewString()` function. It should be updated to use the generic `setutils.New[string]()` instead.

## Files to modify

- `internal/cri/setutils/int.go` - **DELETE** this file
- `internal/cri/setutils/string.go` - **DELETE** this file
- `internal/cri/setutils/set.go` - Remove the `cast` helper function
- `internal/cri/util/strings.go` - Update `MergeStringSlices` to use generic Set

## Verification

After your changes:
- The `internal/cri/setutils` package should compile successfully
- The `internal/cri/util` package should compile successfully
- The `MergeStringSlices` function should continue to work correctly for merging string slices with deduplication

This is an internal package cleanup that doesn't affect the public Go API.
