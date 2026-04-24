# Prerelease config: rename `tag` to `channel` and decouple npm dist-tag

## Problem

The `remix` package's prerelease system couples the version suffix (e.g. `alpha`) directly to the npm dist-tag. This means a version like `3.0.0-alpha.0` gets tagged as `alpha` on npm. The dist-tag should always be `next` regardless of the prerelease channel (alpha, beta, rc). Additionally, the config field name `tag` in `prerelease.json` is confusing since it conflates two separate concepts: the prerelease channel (version suffix) and the npm dist-tag.

## Expected Behavior

### Configuration File
- `packages/remix/.changes/prerelease.json` must use a field named `channel` (not `tag`)
- The `channel` field value is the string `"alpha"` (e.g., `{ "channel": "alpha", ... }`)

### changes.ts — readRemixPrereleaseConfig()
- The `RemixPrereleaseConfig` interface must define `channel: string`
- The function must check for `'channel' in obj` and read `obj.channel`
- The function must validate the channel value with `.trim()` (e.g., `obj.channel.trim()`)
- The function must return an object containing `config: { channel: ... }`

### changes.ts — getNextVersion()
- Version calculation must use `semver.inc`

### publish.ts — Prerelease Publishing
- The script must use the variable `remixPrereleaseChannel` (renamed from the old `tag` variable)
- The publish command for remix must use `--tag next` (not `--tag ${channel}` or any other tag)
- The publish command must be a real `pnpm publish` command

### Documentation
- `AGENTS.md` must mention the `channel` field and explain that the npm dist-tag is always `"next"`
- `CONTRIBUTING.md` must show `prerelease channels` in section headers (not "tags") and include a JSON example with `"channel": "alpha"`

## Files to Modify

- `packages/remix/.changes/prerelease.json` — rename `tag` to `channel`, value remains `"alpha"`
- `scripts/utils/changes.ts` — update RemixPrereleaseConfig interface, readRemixPrereleaseConfig(), and getNextVersion()
- `scripts/publish.ts` — rename tag variable to `remixPrereleaseChannel`, ensure `--tag next` is used
- `AGENTS.md` — update prerelease documentation to use `channel` terminology and explain `next` dist-tag
- `CONTRIBUTING.md` — update prerelease section headers and JSON examples

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
