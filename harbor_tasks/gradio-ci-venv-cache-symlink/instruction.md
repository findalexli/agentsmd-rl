# Broken Symlinks in CI After Python Point-Release

## Bug Description

The GitHub Actions CI pipeline for this repository intermittently fails with broken symlink errors inside the cached virtualenv. The failures correlate with Python receiving a patch-level version bump on the GitHub-hosted runner (e.g., 3.12.7 → 3.12.8).

Symptoms:
- CI jobs fail with "No such file or directory" or broken symlink errors pointing at a Python binary path that no longer exists
- The failures are intermittent — they appear only when the runner image ships a newer Python patch release than what was cached
- Clearing the Actions cache temporarily fixes the issue, but it breaks again on the next Python bump

The root cause is somewhere in `.github/actions/install-all-deps/action.yml`. Look at how the virtualenv is created relative to the cache restore, and what information the cache key uses to distinguish between Python versions.

## Secondary Issue

There is also a flaky frontend test in `js/textbox/Textbox.test.ts`. The test for the copy button's click event sometimes passes and sometimes fails. The test fires a click event and immediately asserts, but the Svelte component needs an event-loop tick to process the event. Look at how similar event tests in the same file handle async timing.

## Relevant Files

- `.github/actions/install-all-deps/action.yml` — the composite action that sets up Python, creates a venv, and restores/saves the cache
- `js/textbox/Textbox.test.ts` — the Textbox component test file with the flaky copy test

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
