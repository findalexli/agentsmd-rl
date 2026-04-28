# Enhance buildkite-failures.ts with log fetching, wait mode, and help text

## Problem

The `scripts/buildkite-failures.ts` script shows BuildKite CI failures for the bun project, but it has several gaps:

1. **No help text**: Running with `--help` or `-h` does nothing useful — new contributors don't know what arguments and options the script accepts.
2. **No log fetching**: When builds fail, developers have to manually navigate to BuildKite's web UI to read logs. The script should fetch and save full job logs locally so they can be searched and reviewed in a terminal.
3. **No wait mode**: There's no way to poll an in-progress build — you have to manually re-run the script until it completes.
4. **Limited failure display**: When no annotations are available, the script just shows a count and a link. It should provide a structured breakdown of failures grouped by type (build/test/other) with error summaries.
5. **No canceled/pending handling**: The script doesn't gracefully handle builds that are scheduled, running, or canceled.

## Expected Behavior

- `--help` / `-h` should print comprehensive usage and exit 0. The help text must include:
  - All supported input formats: build number, branch name, PR URL, and `#number` shorthand
  - The `--wait` flag with explanation of polling behavior (waiting for build completion)
  - The `--flaky` flag for flaky test handling
  - The `--warnings` flag for warning display
  - Documentation that failed job logs are saved to files matching pattern `/tmp/bun-build-{number}-{platform}-{step}.log`

- `--wait` should poll the build status every ~10 seconds and show progress updates until the build completes, fails, or shows failures early.

- Failed job logs should be fetched from BuildKite's public API (buildkite.com) and saved to `/tmp/bun-build-{number}-{platform}-{step}.log`, with a brief error summary shown inline.

- Failures should be grouped by type (build failures, test failures, other) with duration and links.

- Canceled and in-progress builds should display appropriate status messages.

- After making the code changes, **update the project's CLAUDE.md** to document this script's usage so that contributors and AI agents know how to debug CI failures. The documentation should include representative usage examples.

## Files to Look At

- `scripts/buildkite-failures.ts` — the CI failure analysis script that needs enhancement
- `CLAUDE.md` — project instructions for developers and AI agents; should document the enhanced script

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier` (JS/TS/JSON/Markdown formatter)
- `oxlint` (JavaScript/TypeScript linter)
