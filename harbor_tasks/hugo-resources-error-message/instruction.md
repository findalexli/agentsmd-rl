# Improve Error Message for Image Operations on Non-Raster Resources

## Problem

When calling image methods (like `Width`, `Height`, `Resize`, etc.) on SVG resources in Hugo, the error message is not helpful. The code produces generic error messages that don't tell users:

1. Which resource caused the problem
2. What the resource's actual media type is
3. How to properly check if a resource supports image operations before calling them

The old error messages were:
- "this method is only available for raster images" (for SVG files)
- "this method is only available for image resources" (for other non-image resources)

## Task

Modify the `getImageOps` function in `resources/transform.go` to improve the error message when image operations are called on non-raster resources.

## Requirements

1. **Resource identification**: The error message should identify which resource caused the problem.

2. **Media type information**: The error message should show the actual media type of the resource.

3. **Actionable guidance**: The error message should guide users on how to check if a resource supports image operations before calling those methods.

4. **Error message formatting**: Use `fmt.Sprintf` in the code to format error messages with structured context.

5. **Reflection-based type hints**: The error message should reference `reflect.IsImage`-style helpers (such as `reflect.IsImageResource`, `reflect.IsImageResourceProcessable`, `reflect.IsImageResourceWithMeta`) to guide users on how to detect supported resource types programmatically.

6. **Maintain function signature**: The function `func (r *resourceAdapter) getImageOps()` must continue to exist with its original signature.

## Context

This issue affects the Hugo static site generator's resource handling. When template authors call `.Width` or similar methods on an SVG resource (which doesn't have a fixed width/height), they receive an unhelpful error.

The goal is to help template authors understand what went wrong, which resource was involved, and how to prevent the error by checking resource type first.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
