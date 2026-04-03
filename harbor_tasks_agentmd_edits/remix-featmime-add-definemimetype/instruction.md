# Add `defineMimeType` to `@remix-run/mime`

## Problem

The `@remix-run/mime` package provides utilities for detecting MIME types from file extensions, but there is no way to register custom MIME types. Users who work with non-standard file extensions (e.g., `.mdx`, `.prisma`, custom formats) cannot use `detectMimeType`, `isCompressibleMimeType`, or `mimeTypeToContentType` for those extensions. There is also no way to override built-in mappings (e.g., `.ts` maps to `video/mp2t` rather than `text/typescript`).

See: https://github.com/remix-run/remix/issues/10918

## Expected Behavior

The package should export a `defineMimeType()` function that allows registering custom MIME type definitions. A registration should support:

- Mapping one or more file extensions to a MIME type
- Optionally specifying whether the type is compressible
- Optionally specifying a charset for Content-Type headers

Custom registrations should take precedence over built-in types across all existing utility functions (`detectMimeType`, `isCompressibleMimeType`, `mimeTypeToContentType`, `detectContentType`).

After implementing the feature, update the package's README to document the new API, and create a changeset file for the release.

## Files to Look At

- `packages/mime/src/index.ts` — public API exports for the package
- `packages/mime/src/lib/detect-mime-type.ts` — resolves file extensions to MIME types
- `packages/mime/src/lib/is-compressible-mime-type.ts` — checks MIME type compressibility
- `packages/mime/src/lib/mime-type-to-content-type.ts` — converts MIME type to Content-Type with charset
- `packages/mime/README.md` — package documentation
- `AGENTS.md` — repo-wide development guidelines (see Changes and Releases section)
