# Smarter changelog generation

## Problem

The changelog generation pipeline is monolithic: `script/changelog.ts` handles everything — fetching commits from GitHub, grouping by area, filtering, formatting, and contributor lists. This makes it hard to maintain and prevents the project from leveraging its own AI agent for the actual changelog writing.

The `.opencode/command/changelog.md` command template needs updating to match the new architecture and provide better guidance about writing user-focused entries.

## Expected Behavior

Refactor the changelog system into two separate scripts:
1. Extract the raw data generation logic (commit fetching, grouping, filtering, contributor handling) into a new `script/raw-changelog.ts`
2. Convert `script/changelog.ts` into a thin wrapper that delegates changelog writing to the AI agent via `opencode run --command changelog`

The thin wrapper should handle:
- Deleting the existing `UPCOMING_CHANGELOG.md` before regenerating
- Accepting `--variant`, `--quiet`, and `--print` flags
- Spawning the opencode process and handling its output

Update `script/version.ts` to call `bun script/changelog.ts` directly instead of going through `opencode run --command changelog`.

Update `.opencode/command/changelog.md` to:
- Use the new raw data script as its input source
- Add guidance about understanding flow-on effects for users (e.g., a package upgrade that patches a user-facing bug)
- Wrap the input section in XML-style tags
- Emphasize being concise since users skim the changelog

## Files to Look At

- `script/changelog.ts` — the monolithic changelog script to refactor
- `.opencode/command/changelog.md` — the agent command template for changelog generation
- `script/version.ts` — the release versioning script that invokes changelog generation
