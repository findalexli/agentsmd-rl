# Improve Error Message for Image Operations on Non-Raster Resources

## Problem

When calling image methods (like `Width`, `Height`, `Resize`, etc.) on SVG resources in Hugo, the error message is not helpful. Currently, the code produces generic error messages that don't tell users:

1. Which resource caused the problem
2. What the resource's actual media type is
3. How to properly check if a resource supports image operations before calling them

The old error messages were:
- "this method is only available for raster images" (for SVG files)
- "this method is only available for image resources" (for other non-image resources)

## Task

Modify the `getImageOps` function in `resources/transform.go` to improve the error message when image operations are called on non-raster resources.

The error message should provide:

1. **Resource identification**: Include the resource name
2. **Media type information**: Show the actual media type of the resource
3. **Actionable guidance**: Tell users which reflection methods to use for checking resource capabilities

## Requirements

1. **New error message format**: The error message must use `fmt.Sprintf` and include both the resource name and media type. Use quoted format verbs (`%q`) for the resource name and media type.

2. **Reflection method hints**: The error message must reference these three reflection methods:
   - `reflect.IsImageResource`
   - `reflect.IsImageResourceProcessable`
   - `reflect.IsImageResourceWithMeta`

3. **Removed old messages**: The following old error patterns must be removed from the code:
   - "this method is only available for raster images"
   - "this method is only available for image resources"
   - `if eq .MediaType.SubType "svg"` (SVG type check pattern)

4. **Maintain function signature**: The function `func (r *resourceAdapter) getImageOps()` must continue to exist with its original signature.

## Context

This issue affects the Hugo static site generator's resource handling. When template authors call `.Width` or similar methods on an SVG resource (which doesn't have a fixed width/height), they receive an unhelpful error.

The goal is to help template authors understand:
- What went wrong (they called an image method on a non-raster resource)
- Which resource was involved
- How to prevent the error by checking resource type first using the reflection methods
