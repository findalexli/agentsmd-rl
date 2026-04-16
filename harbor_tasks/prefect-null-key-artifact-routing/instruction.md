# Fix Null-Key Artifact Routing in ArtifactCard

## Problem

The `ArtifactCard` component in the Prefect UI v2 always links to `/artifacts/key/$key`, using an empty string fallback when `artifact.key` is null. This produces a broken route (`/artifacts/key/`) for artifacts that don't have a key.

When viewing flow-run or task-run artifact tabs, null-key artifacts appear but clicking them results in a broken navigation because the route expects a key parameter.

## Location

- **Primary file**: `ui-v2/src/components/artifacts/artifact-card.tsx`
- **Test file**: `ui-v2/src/components/artifacts/artifact-card.test.tsx`

## Required Behavior

Your fix must ensure the following specific behaviors:

### 1. Route Selection Logic

The component must conditionally choose between two Tanstack Router routes based on whether `artifact.key` exists:

- **When `artifact.key` is truthy** (non-null, non-empty string): Link to `"/artifacts/key/$key"` with the key passed as the `key` parameter
- **When `artifact.key` is falsy** (null, undefined, or empty string): Link to `"/artifacts/artifact/$id"` with the artifact ID passed as the `id` parameter

### 2. Artifact vs ArtifactCollection Handling

The component receives either an `Artifact` or `ArtifactCollection` object. When routing by ID (for null-key artifacts), you must handle both types:

- `ArtifactCollection` objects have a `latest_id` field - use this when present
- `Artifact` objects have an `id` field - use this when `latest_id` is not present
- Use duck-typing with `"latest_id" in artifact` to distinguish between the types

### 3. Remove Broken Pattern

The old pattern `params={{ key: artifact.key ?? "" }}` that causes the broken `/artifacts/key/` route must be removed.

## Expected Behavior

1. When `artifact.key` is **truthy** (non-null, non-empty string), the card should link to `/artifacts/key/$key`.
2. When `artifact.key` is **falsy** (null, undefined, or empty string), the card should link to `/artifacts/artifact/$id` instead.
3. The fix should correctly handle both `Artifact` and `ArtifactCollection` types.

## Constraints

- Follow the existing code patterns in the repository
- Run `npm run check` and `npm test -- artifact-card` to verify
- Do not use `as unknown` type assertions
- Do not use `eslint-disable` comments

## Testing

The repository uses Vitest with React Testing Library. You can run:

```bash
cd ui-v2
npm test -- artifact-card
```

The test file already has existing tests you can use as a reference for expected patterns.

## Notes

- The component currently uses a `Link` component from Tanstack Router
- The current implementation always passes `params={{ key: artifact.key ?? "" }}`
- Collections index page already excludes null-key artifacts server-side, but flow-run/task-run views show them
