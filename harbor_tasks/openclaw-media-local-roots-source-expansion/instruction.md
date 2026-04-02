# Media Local Roots Widened by Untrusted Source Paths

## Bug Report

The media pipeline's local file access allowlist can be widened by arbitrary media source paths, creating a path traversal vector. When a media tool processes sources (images, videos, etc.), the parent directories of those source paths are implicitly added to the allowed local roots, effectively giving the caller access to any directory on the filesystem.

### Problem

In `src/media/local-roots.ts`, the function `appendLocalMediaParentRoots()` takes the current set of allowed roots plus a list of media source paths, then appends the parent directory of each local source path to the allowed roots. This means:

- A media source of `/Users/peter/Pictures/photo.png` adds `/Users/peter/Pictures` to allowed roots
- A `file://` URL pointing to `/Users/peter/Movies/clip.mp4` adds `/Users/peter/Movies`
- Only filesystem-root parents (e.g., `/`) are filtered out

This expansion is consumed by:
1. `resolveMediaToolLocalRoots()` in `src/agents/tools/media-tool-shared.ts` — used by media tools to determine which local paths they can access
2. `getAgentScopedMediaLocalRootsForSources()` in `src/media/local-roots.ts` — used by agent-scoped media operations

Both functions pass untrusted `mediaSources` arrays through to `appendLocalMediaParentRoots`, widening the allowed roots based on input data rather than configuration.

### Expected Behavior

Local media roots should be derived only from explicit configuration (default roots, workspace directory, agent-scoped state directories). Media source paths in requests should not influence which directories the system is allowed to access.

### Relevant Files

- `src/media/local-roots.ts` — root expansion logic and agent-scoped root resolution
- `src/agents/tools/media-tool-shared.ts` — media tool root resolution, calls into `local-roots.ts`
- `src/media/local-roots.test.ts` — existing test coverage for local roots
- `src/agents/tools/media-tool-shared.test.ts` — (may not exist yet) test coverage for media tool roots
