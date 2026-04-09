# Improve Error Message for Image Operations on Non-Raster Resources

## Problem

When calling image methods (like `Width`, `Height`, `Resize`, etc.) on SVG resources in Hugo, the error message is not helpful. Currently, the code panics with either:

- "this method is only available for raster images" (for SVG files)
- "this method is only available for image resources" (for other non-image resources)

This doesn't tell users:
1. Which resource caused the problem
2. What the resource's actual media type is
3. How to properly check if a resource supports image operations before calling them

## Task

Improve the error message in the `getImageOps()` method in `resources/transform.go` to provide:

1. **Resource identification**: Include the resource name in the error
2. **Media type information**: Show the actual media type of the resource
3. **Actionable guidance**: Tell users which reflection methods to use for checking resource capabilities (`reflect.IsImageResource`, `reflect.IsImageResourceProcessable`, `reflect.IsImageResourceWithMeta`)

The error should use `fmt.Sprintf` to format a message like:
```
resource "<name>" of media type "<type>" does not support this method: use reflect.IsImageResource, reflect.IsImageResourceProcessable, or reflect.IsImageResourceWithMeta to check if the resource supports this method before calling it
```

## Files to Modify

- `resources/transform.go` - Update the `getImageOps()` method on the `resourceAdapter` type

## Testing

The relevant test is in `resources/resources_integration_test.go` - look for the test that checks the error message when calling `Width` on an SVG resource.

When running the tests with `go test -v -run TestSVGResource ./resources/...`, the test should pass after your changes.

## Context

The `getImageOps()` method is called by various image operation methods on resources. When a user template calls `.Width` or similar methods on an SVG (which doesn't have a fixed width/height), this code path is triggered.

The goal is to help template authors understand:
- What went wrong (they called an image method on a non-raster resource)
- Which resource was involved
- How to prevent the error by checking resource type first
