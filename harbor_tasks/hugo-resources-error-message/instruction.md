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

Find the code in the Hugo repository that handles image operations on resources and improve the error message to provide:

1. **Resource identification**: Include the resource name in the error
2. **Media type information**: Show the actual media type of the resource
3. **Actionable guidance**: Tell users which reflection methods to use for checking resource capabilities

The improved error message should reference these three reflection methods:
- `reflect.IsImageResource`
- `reflect.IsImageResourceProcessable`
- `reflect.IsImageResourceWithMeta`

The error message should use `fmt.Sprintf` for formatting and follow Go conventions for error messages with quoted strings (using `%q` verb or similar).

## Requirements

- The old error messages "this method is only available for raster images" and "this method is only available for image resources" should no longer be used
- The improved error message should include the resource name and media type
- The improved error message should mention the three reflection helper methods
- Use `fmt.Sprintf` to format the error message

## Context

This issue affects the Hugo static site generator's resource handling. When template authors call `.Width` or similar methods on an SVG resource (which doesn't have a fixed width/height), they receive an unhelpful error.

The goal is to help template authors understand:
- What went wrong (they called an image method on a non-raster resource)
- Which resource was involved
- How to prevent the error by checking resource type first using the reflection methods
