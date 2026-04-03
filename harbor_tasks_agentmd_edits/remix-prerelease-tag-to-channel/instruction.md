# Decouple remix prerelease channel from npm dist-tag

## Problem

The `remix` package's prerelease publishing system currently couples two concepts together: the prerelease "tag" (e.g. `alpha`, `beta`, `rc`) is used both as the version suffix AND as the npm dist-tag. This means publishing `3.0.0-alpha.0` also uses `alpha` as the npm dist-tag.

The desired behavior is to decouple these: the prerelease identifier (alpha/beta/rc) should only determine the version suffix, while all prereleases should always be published to npm under the `next` dist-tag.

## Expected Behavior

1. `packages/remix/.changes/prerelease.json` should use a field name that reflects it controls the version channel (not the npm tag)
2. The publish script (`scripts/publish.ts`) should always use `next` as the npm dist-tag for remix prereleases, regardless of which prerelease channel is active
3. The config reader (`scripts/utils/changes.ts`) — including the `RemixPrereleaseConfig` interface, validation logic, error messages, and version calculation — should use consistent terminology matching the new field name
4. The project's documentation files (`AGENTS.md`, `CONTRIBUTING.md`) should be updated to reflect the new terminology and behavior. This includes updating JSON examples, section headers, and explanatory text about how prerelease publishing works.

## Files to Look At

- `packages/remix/.changes/prerelease.json` — prerelease mode configuration
- `scripts/utils/changes.ts` — config reader, validator, and version calculator
- `scripts/publish.ts` — npm publishing logic
- `AGENTS.md` — developer guide with prerelease documentation
- `CONTRIBUTING.md` — contributor guide with prerelease instructions
