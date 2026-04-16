# Task: Add --library-push flag to containers registries credentials

## Problem

The `wrangler containers registries credentials` command currently supports two permission flags:
- `--pull` — for pulling images from a registry
- `--push` — for pushing images to a registry

A third permission type is needed: the ability to push to the public library namespace. This should be exposed as a `--library-push` flag. Because this permission is for internal use only, the flag must be hidden from CLI help output.

## Requirements

When the user provides the `--library-push` flag, the command should grant credentials with permission to push to the public library namespace. The new flag should behave consistently with the existing `--push` and `--pull` flags:

1. The CLI argument should be named `library-push` and be a boolean type. It should be hidden from help output since it's for internal use only.

2. The permission string sent to the API when this flag is used should be `library_push` (following the snake_case convention where `--push` sends `push` and `--pull` sends `pull`).

3. The `ImageRegistryPermissions` enum (located at `packages/containers-shared/src/client/models/ImageRegistryPermissions.ts`) needs a new member for the library push permission. Following the pattern of the existing `PULL = "pull"` and `PUSH = "push"` members, add a member with:
   - An enum key of `LIBRARY_PUSH`
   - A string value of `"library_push"`

4. The `registryCredentialsCommand` function in `packages/wrangler/src/containers/registries.ts` needs to:
   - Accept a `libraryPush` parameter (boolean, optional) in its arguments
   - Include this parameter in the validation that checks at least one permission flag is provided
   - Pass the `"library_push"` string to the permissions array when the flag is set

5. The validation error message should continue to mention only `--push` and `--pull` (no need to expose the hidden flag in user-facing errors).

## Testing

Run the containers registries tests to verify your changes:
```bash
pnpm run test:ci --filter wrangler -- containers/registries
```

You can also type-check the changes:
```bash
pnpm run check:type --filter wrangler
```
