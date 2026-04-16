# File-based Route Generation Fails with Custom Token Prefixes

## Problem

The TanStack Router file-based route generator produces incorrect route paths when using custom `indexToken` or `routeToken` configuration values that contain regex metacharacters.

For example, configuring the generator to use `+page` as the index token or `+layout` as the route token causes incorrect path generation. With `indexToken: { regex: "\\+page" }`, nested routes like `dashboard/+page.tsx` incorrectly get path `/dashboard/+page` instead of `/dashboard/`. Similarly, with `routeToken: { regex: "\\+layout" }`, layout routes like `dashboard/+layout.tsx` incorrectly get path `/dashboard/+layout` instead of `/dashboard`.

## Reproduction

1. Create a routes directory with files named using special character prefixes:
   ```
   routes/
   ├── __root.tsx
   ├── +page.tsx           # index route
   └── dashboard/
       ├── +layout.tsx     # layout route
       └── +page.tsx       # dashboard index
   ```

2. Configure `tsr.config.json`:
   ```json
   {
     "indexToken": { "regex": "\\+page" },
     "routeToken": { "regex": "\\+layout" }
   }
   ```

3. Run the route generator - the generated route tree will have incorrect paths where the token suffix isn't properly stripped.

## Expected Behavior

The generator should export an `escapeRegExp` function from `packages/router-generator/src/utils.ts` that escapes regex metacharacters in token strings. This function must escape all regex metacharacters including: `+`, `*`, `?`, `.`, `(`, `)`, `[`, `]`, `$`, `^`, `|`, and `\`.

For example:
- `escapeRegExp('+page')` should return `'\\+page'`
- `escapeRegExp('*index')` should return `'\\*index'`
- `escapeRegExp('route.config')` should return `'route\\.config'`

When properly implemented, the generator should produce correct paths with tokens fully stripped:
- `dashboard/+page.tsx` with `indexToken: { regex: "\\+page" }` should generate path `/dashboard/`
- `dashboard/+layout.tsx` with `routeToken: { regex: "\\+layout" }` should generate path `/dashboard`
- Files with `*index`, `?layout`, or other metacharacter prefixes should similarly have those prefixes stripped from the generated route paths

## Relevant Files

- `packages/router-generator/src/filesystem/physical/getRouteNodes.ts` - Main route node processing logic
- `packages/router-generator/src/utils.ts` - Utility functions (where `escapeRegExp` must be exported)

## Notes

The issue occurs because the generator uses token values as literal strings in regular expression patterns without escaping. When tokens contain regex metacharacters like `+`, `*`, `?`, etc., the resulting regex patterns match incorrectly or fail to strip the token from the path.
