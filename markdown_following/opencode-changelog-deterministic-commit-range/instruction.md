# Bug: Release changelogs are shifted by one version

## Problem

When generating release changelogs, the output for version N actually contains the changes from version N-1. For example, the changelog for v1.3.5 shows the changes that were in v1.3.4.

There are two root causes:

1. **Non-deterministic commit range**: The changelog generation relies on an LLM (via the `@opencode-ai/sdk` and `@opencode-ai/script` packages) to fetch the latest GitHub release, find merged PRs, and build a commit list. The LLM improvises the commit range rather than computing it deterministically, leading to off-by-one version errors.

2. **Missing upper bound in release workflow**: The release workflow calls the changelog command without pinning the upper bound of the commit range. This means commits that land after the release cut can leak into the changelog.

## Files to modify

- `script/changelog.ts` — The main changelog generation script
- `script/version.ts` — The version/release workflow script
- `.opencode/command/changelog.md` — The LLM command prompt for changelog generation
- `.gitignore` — Git ignore patterns

## Constraints from AGENTS.md

When modifying `script/changelog.ts` and `script/version.ts`, you MUST follow these rules:

1. **No try/catch blocks** (AGENTS.md line 12): Do not use try/catch for control flow. Restructure logic to handle errors without exception handling.

2. **Single-word function names** (AGENTS.md lines 27-32): All declared functions must use single-word lowercase names (e.g., `latest`, `diff`, `commits`). Multi-word camelCase function names like `getLatestRelease`, `getCommits`, `filterRevertedCommits` are prohibited.

3. **No camelCase local variables** (AGENTS.md lines 27-32): Local variable declarations must use single-word names. Multi-word camelCase locals like `fromRef`, `toRef`, `commitData`, `sectionOrder`, `revertPattern` are prohibited.

4. **No `any` type** (AGENTS.md line 13): Explicit types only.

## Expected behavior

- The `script/changelog.ts` script must gather commits deterministically using `gh api` and `git log`, group them into sections, filter reverts, identify community contributors, and output structured text directly. It must not import or use any LLM SDK packages for commit summarization.

- The help text for `script/changelog.ts --help` must distinguish between draft and non-draft releases when describing the default starting version. The base help says "Starting version (default: latest GitHub release)" which does not distinguish draft vs non-draft.

- The `script/version.ts` script must pin the commit range upper bound at the release point when invoking the changelog command, so that commits landing after the release cut cannot leak into the changelog.

- The `.opencode/command/changelog.md` prompt must not instruct the LLM to fetch GitHub releases or find PRs. The command should consume pre-computed structured data piped from `script/changelog.ts` rather than having the LLM gather this information itself.

- The generated changelog file (name contains "UPCOMING_CHANGELOG") must be listed in `.gitignore` so it is not accidentally committed.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
