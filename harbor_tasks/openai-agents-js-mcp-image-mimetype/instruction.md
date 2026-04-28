# Task: Fix MCP image output handling for mimeType field

## Context

The OpenAI Agents JS SDK is a TypeScript monorepo that provides agent orchestration with MCP (Model Context Protocol) support. When MCP tools return image outputs, the SDK normalizes them into a format compatible with the OpenAI Responses API.

## Problem

MCP tools can return image outputs using `mimeType` as the field name for the media type (e.g., `"image/jpeg"`). The SDK currently only recognizes the `mediaType` field name when normalizing image tool outputs. When an MCP tool returns an image with `mimeType` instead of `mediaType`, the SDK falls through without extracting the media type and forwards raw base64 data into the OpenAI API `image_url` field. This triggers a **400 validation error** from the OpenAI API because the `image_url` field expects a proper `data:<mime>;base64,...` data URL, not bare base64.

The issue manifests in two code paths:

1. **Core tool execution**: The `normalizeStructuredToolOutput` function checks `mediaType` on tool output objects but ignores `mimeType`. The `convertStructuredToolOutputToInputItem` function has the same gap for nested image objects.

2. **OpenAI Responses adapter**: The `convertLegacyToolOutputContent` function uses `getImageInlineMediaType` which only checks `mediaType`, missing `mimeType`. Additionally, when image data is extracted from a top-level `data` field (not inside a nested `image` object), the raw base64 is assigned directly without formatting it into a data URL, even when a top-level mimeType is available.

## Expected behavior

When an MCP tool returns image output with `mimeType` (e.g., `{ type: "image", data: "<base64>", mimeType: "image/jpeg" }`), the SDK should:

- Recognize `mimeType` as an alias for `mediaType` in both top-level and nested image output objects
- Convert the base64 data into a proper `data:image/jpeg;base64,<data>` data URL
- Preserve already-formatted data URLs without double-wrapping (i.e., if data starts with `data:`, don't prepend another `data:...;base64,` prefix)
- Fall back to top-level `mimeType` when a nested image object doesn't have its own media type

This must work for both:
- Top-level format: `{ type: "image", data: "<base64>", mimeType: "image/png" }`
- Nested format: `{ type: "image", image: { data: "<base64>", mimeType: "image/gif" } }`

## Code Style Requirements

This project uses ESLint for code style enforcement. Run `pnpm lint` to verify your changes meet the project's style rules. The lint check must pass for all changed files.

## Testing

After making changes, run:
- `pnpm build` to verify the build succeeds
- `pnpm lint` to verify linting passes
- `CI=1 pnpm test` to verify all existing tests pass
- Add unit tests in the relevant package test directories (`packages/<pkg>/test/`) covering the `mimeType` handling
