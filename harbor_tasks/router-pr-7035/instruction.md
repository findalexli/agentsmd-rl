# Fix Missing Declaration Files for Server Entry Exports

The `server-entry` export in `@tanstack/react-start`, `@tanstack/solid-start`, and `@tanstack/vue-start` packages has broken TypeScript declaration files.

## Symptom

After building these packages, the `server-entry` export's declaration files are emitted at an incorrect nested path. The package.json exports declare the types at:

```
dist/default-entry/esm/server.d.ts
```

But the actual declaration files are being generated at a deeply nested path that doesn't match the export declaration.

## Impact

Users importing from the `server-entry` export get TypeScript errors because the `.d.ts` files aren't where package.json says they should be:

```typescript
import { ... } from '@tanstack/react-start/server-entry'
// Error: Could not find declaration file
```

## Affected Packages

- `packages/react-start/`
- `packages/solid-start/`
- `packages/vue-start/`

## Relevant Files

Each affected package has:
- `vite.config.server-entry.ts` - Vite configuration for building the server entry point
- `tsconfig.json` - Base TypeScript configuration

## Investigation Hints

- Look at how other vite configs in the same packages handle TypeScript declaration output paths
- Check how `vite-plugin-dts` determines the output structure
- Compare with packages that have working declaration file paths (e.g., the main `src/` entry point)
