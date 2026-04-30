# Add AGENTS.md file

Source: [brave/brave-core#35409](https://github.com/brave/brave-core/pull/35409)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- Add brave-browser issue below that this PR will resolve -->
Resolves https://github.com/brave/brave-browser/issues/54370

I used a textual reference rather than a symlink since symlinks seem to have slightly different behavior on Windows. This should be the most compatible approach.

<!-- CI-related labels that can be applied to this PR:
* CI/disable-pipeline-step-cache - instruct CI to not cache build steps between runs for the same commit hash
* CI/enable-coverage - enable coverage reporting for your code changes
* CI/enable-test-only-affected - instruct CI to only run tests affected by your change
* CI/run-audit-deps (1) - check for known npm/cargo vulnerabilities (audit_deps)
* CI/run-network-audit (1) - run network-audit
* CI/run-perf-smoke-tests - run smoke performance tests
* CI/storybook-url (1) - deploy storybook and provide a unique URL for each build
* CI/run-upstream-tests - run Chromium unit and browser tests on Linux and Windows (otherwise only on Linux)
* CI/skip-upstream-tests - do not run Chromium unit, or browser tests (otherwise only on Linux)
* CI/run-teamcity - run TeamCity
* CI/skip-teamcity - skip TeamCity
* CI/skip - do not run CI builds (except noplatform)
* CI/run-linux-arm64, CI/run-macos-x64, CI/run-windows-arm64, CI/run-windows-x86 - run builds that would otherwise be skipped
* CI/skip-linux-x64, CI/skip-android, CI/skip-macos-arm64, CI/skip-ios, CI/skip-windows-x64 - skip CI builds for specific platforms

(1) applied aut

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
