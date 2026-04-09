# Fix plugin specifier parsing for complex package formats

## Problem

`parsePluginSpecifier()` in `packages/opencode/src/plugin/shared.ts` incorrectly parses package specifiers that contain multiple `@` characters or use the `npm:` protocol prefix.

Specifically:

- **git+ssh URLs**: A specifier like `acme@git+ssh://git@github.com/org/repo.git` is split at the wrong `@`, producing a garbled package name (`acme@git+ssh://git`) and wrong version (`github.com/org/repo.git`).
- **Bare npm: protocol**: `npm:@scope/package@1.0.0` retains the `npm:` prefix in the package name instead of extracting `@scope/package`.
- **Unversioned npm: protocol**: `npm:@scope/package` splits at the scope `@`, yielding `npm:` as the package name.
- **npm aliases**: `mypkg@npm:@scope/package@1.0.0` splits at the last `@`, corrupting the package name.

On Windows, plugin cache paths derived from specifiers containing `:` or other illegal filesystem characters also cause failures.

## Expected Behavior

`parsePluginSpecifier(spec)` should return `{ pkg, version }` where `pkg` is the clean package name and `version` is the version/URL specifier. It must handle scoped packages, git URLs, npm protocol specifiers, and aliases correctly.

## Files to Look At

- `packages/opencode/src/plugin/shared.ts` — contains `parsePluginSpecifier()` and `resolvePluginTarget()`
- `packages/opencode/src/npm/index.ts` — contains the cache `directory()` helper that builds filesystem paths from package names
