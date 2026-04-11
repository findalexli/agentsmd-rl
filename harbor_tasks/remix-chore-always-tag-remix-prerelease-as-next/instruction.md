# Prerelease config: rename `tag` to `channel` and decouple npm dist-tag

## Problem

The `remix` package's prerelease system couples the version suffix (e.g. `alpha`) directly to the npm dist-tag. This means a version like `3.0.0-alpha.0` gets tagged as `alpha` on npm. The dist-tag should always be `next` regardless of the prerelease channel (alpha, beta, rc). Additionally, the config field name `tag` in `prerelease.json` is confusing since it conflates two separate concepts: the prerelease channel (version suffix) and the npm dist-tag.

## Expected Behavior

- The `prerelease.json` config field should be renamed from `tag` to `channel` to clearly distinguish it from the npm dist-tag
- The npm dist-tag for remix prereleases should always be `"next"`, regardless of the channel value
- The code in `scripts/utils/changes.ts` and `scripts/publish.ts` should use the new `channel` terminology
- The project documentation (`AGENTS.md`, `CONTRIBUTING.md`) should be updated to reflect the renamed field and the fact that the dist-tag is always `next`

## Files to Look At

- `packages/remix/.changes/prerelease.json` — the prerelease config file (currently uses `"tag"`)
- `scripts/utils/changes.ts` — contains `RemixPrereleaseConfig` interface and `readRemixPrereleaseConfig()` which reads/validates the config
- `scripts/publish.ts` — the publish script that uses the prerelease config to determine the npm tag
- `AGENTS.md` — development guide with prerelease documentation (look for the "Prerelease mode" section under "Changes and Releases")
- `CONTRIBUTING.md` — contributor guide with prerelease instructions

After fixing the code, update `AGENTS.md` and `CONTRIBUTING.md` to reflect the renamed field and the new behavior where the npm dist-tag is always `"next"`.
