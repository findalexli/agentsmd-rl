# Decouple remix prerelease channel from npm dist-tag

## Problem

The `remix` package's prerelease publishing system currently couples two separate concepts: the prerelease identifier (e.g. `alpha`, `beta`, `rc`) is used both as the version suffix AND as the npm dist-tag. This means publishing `3.0.0-alpha.0` uses `alpha` as the npm dist-tag, but the desired behavior is for all prereleases to always publish under the `next` dist-tag regardless of channel.

The config field name in `packages/remix/.changes/prerelease.json` currently says `"tag"`, which is misleading since it should only control the version channel, not the npm tag.

## Expected Behavior

1. Rename the config field in `packages/remix/.changes/prerelease.json` from `"tag"` to a name that reflects it controls the prerelease version channel
2. Update the config reader and validator in `scripts/utils/changes.ts` to match — interface, field access, error messages, and version calculation logic
3. Update `scripts/publish.ts` to always publish remix prereleases with the `next` npm dist-tag instead of using the prerelease identifier as the tag
4. Update the project's agent instructions and contributor documentation to reflect the new terminology and publishing behavior

## Files to Look At

- `packages/remix/.changes/prerelease.json` — prerelease mode configuration
- `scripts/utils/changes.ts` — config reader, validator, and version calculator
- `scripts/publish.ts` — npm publishing logic
- `AGENTS.md` — developer guide with prerelease documentation (Changes and Releases section)
- `CONTRIBUTING.md` — contributor guide with prerelease instructions
