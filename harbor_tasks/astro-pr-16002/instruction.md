# Fix File Descriptor Leaks from Read Streams

## Problem

The Astro monorepo (`/workspace/astro`) has file descriptor leaks in two packages under `packages/integrations/`. When clients disconnect or errors occur during file serving, open file descriptors are not released, which can exhaust system resources over time.

## Affected Files

- `packages/integrations/partytown/src/sirv.ts` — static file serving for the partytown integration
- `packages/integrations/node/src/serve-app.ts` — error-page reading in the node integration

## What You Need to Do

Fix the file descriptor leaks in both files. Each file's stream handling must include the following patterns to properly release file descriptors on close/error:

### `packages/integrations/partytown/src/sirv.ts`
- The read stream must be captured in a variable: `const stream = fs.createReadStream(file, opts)`
- The stream must pipe to the response: `stream.pipe(res)`
- The stream must be destroyed when the response closes: `res.on('close', () => stream.destroy())`

### `packages/integrations/node/src/serve-app.ts`
- The stream variable must be declared outside the try block: `let stream: ReturnType<typeof createReadStream> | undefined`
- The stream must be assigned inside the try block: `stream = createReadStream(fullPath)`
- The stream must be destroyed in the catch block: `stream?.destroy()`

## Constraints

- The fix must not change normal control flow — only cleanup paths
- TypeScript must compile without errors in both affected packages
- Biome linting must pass on the modified source files
- The repo's standard build (`pnpm run build:ci`) must succeed for both packages
- Existing unit tests must continue to pass
