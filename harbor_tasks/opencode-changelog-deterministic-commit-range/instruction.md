# Bug: Release changelogs are shifted by one version

## Problem

When generating release changelogs, the output for version N actually contains the changes from version N-1. For example, the changelog for v1.3.5 shows the changes that were in v1.3.4.

There are two root causes:

1. **Non-deterministic commit range**: The changelog generation relies on an LLM (via the `@opencode-ai/sdk` and `@opencode-ai/script` packages) to fetch the latest GitHub release, find merged PRs, and build a commit list. The LLM improvises the commit range rather than computing it deterministically, leading to off-by-one version errors.

2. **Missing upper bound in release workflow**: The release workflow calls the changelog command without pinning the upper bound of the commit range. This means commits that land after the release cut can leak into the changelog.

## Constraints from AGENTS.md

When modifying the changelog and version scripts, you MUST follow these rules:

1. **No try/catch blocks** (AGENTS.md line 12): Do not use try/catch for control flow. Restructure logic to handle errors without exception handling.

2. **Single-word function names** (AGENTS.md lines 27-32): All declared functions must use single-word lowercase names (e.g., `latest`, `diff`, `commits`). Multi-word camelCase function names like `getLatestRelease`, `getCommits`, `filterRevertedCommits` are prohibited.

3. **No camelCase local variables** (AGENTS.md lines 27-32): Local variable declarations must use single-word names. Multi-word camelCase locals like `fromRef`, `toRef`, `commitData`, `sectionOrder`, `revertPattern` are prohibited.

4. **No `any` type** (AGENTS.md line 13): Explicit types only.

## Expected behavior

- The changelog generation script must not import or use `@opencode-ai/sdk`, `@opencode-ai/script`, or any LLM-based summarization. It should gather commits deterministically using `gh api` and `git log`, group them into sections, filter reverts, identify community contributors, and output structured text directly.

- The help text for the changelog script must mention "non-draft" when describing the default starting version (e.g., "Starting version (default: latest non-draft GitHub release)").

- The changelog command prompt must not instruct the LLM to fetch GitHub releases or find PRs. It should instead consume pre-computed structured data piped from the changelog script via shell interpolation.

- The release workflow must read the `GITHUB_SHA` environment variable and pass it as a `--to` flag when invoking the changelog command, pinning the commit range upper bound at the release point.

- The generated `UPCOMING_CHANGELOG.md` file must be listed in `.gitignore` so it is not accidentally committed.
