# Add `defineMimeType` to the `@remix-run/mime` package

## Problem

The `@remix-run/mime` package can detect MIME types for known file extensions, but there is no way to register custom MIME types for extensions that aren't in the built-in database. Users who work with proprietary or experimental file formats (e.g., `.myformat`, `.mdx`) cannot use the existing detection functions for these types.

## Expected Behavior

Implement a new `defineMimeType()` function that allows registering custom MIME types for file extensions. It should support:

- Registering a new extension-to-MIME-type mapping
- Overriding built-in mappings (custom registrations take precedence)
- Optionally specifying whether the MIME type is compressible
- Optionally specifying a charset for the Content-Type header
- Multiple extensions per registration
- Extension normalization (lowercase, trim whitespace, strip leading dots)

The custom registrations must integrate with the existing functions: `detectMimeType()`, `isCompressibleMimeType()`, `mimeTypeToContentType()`, and `detectContentType()`.

## Files to Look At

- `packages/mime/src/lib/` — existing MIME type utility modules (`detect-mime-type.ts`, `is-compressible-mime-type.ts`, `mime-type-to-content-type.ts`)
- `packages/mime/src/index.ts` — public API exports for the package
- `packages/mime/README.md` — API documentation that should be updated to document the new function
