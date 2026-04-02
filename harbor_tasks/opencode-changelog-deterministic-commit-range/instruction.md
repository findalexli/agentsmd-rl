# Bug: Release changelogs are shifted by one version

## Problem

When generating release changelogs, the output for version N actually contains the changes from version N-1. For example, the changelog for v1.3.5 shows the changes that were in v1.3.4.

There are two root causes:

1. **Non-deterministic commit range in `script/changelog.ts`**: The changelog generation script delegates too much responsibility to the LLM. It currently asks the LLM (via the opencode SDK) to fetch the latest GitHub release, find merged PRs, and summarize them. The LLM improvises the commit range rather than computing it deterministically, leading to off-by-one version errors.

2. **Missing upper bound in `script/version.ts`**: The release workflow in `script/version.ts` calls the changelog command without pinning the upper bound of the commit range. This means commits that land after the release cut can leak into the changelog.

## Where to look

- `script/changelog.ts` — The main changelog generation script. It currently imports and uses `@opencode-ai/sdk` and `@opencode-ai/script` to have the LLM summarize commits. The commit gathering, section grouping, revert filtering, and contributor attribution should all be computed deterministically by the script itself, with the LLM only responsible for summarizing the final structured output.

- `script/version.ts` — The release version script. It calls `opencode run --command changelog` but doesn't pass a `--to` flag to pin the commit range upper bound to the current `GITHUB_SHA`.

- `.opencode/command/changelog.md` — The opencode command prompt that the LLM follows. It currently instructs the LLM to fetch releases, find PRs, and build the commit list itself. It should instead consume pre-computed structured data from `script/changelog.ts` via shell interpolation.

- `.gitignore` — The generated `UPCOMING_CHANGELOG.md` file should be git-ignored.

## Expected behavior

- `script/changelog.ts` should deterministically gather commits using `gh api` and `git log`, group them into sections, filter reverts, identify community contributors, and output structured text — without using the opencode SDK or LLM for any of this.
- `script/version.ts` should pass `--to <GITHUB_SHA>` when invoking the changelog command so the commit range is pinned.
- `.opencode/command/changelog.md` should consume the structured output from `script/changelog.ts` via shell interpolation (`!bun script/changelog.ts ...`) rather than querying GitHub itself.
