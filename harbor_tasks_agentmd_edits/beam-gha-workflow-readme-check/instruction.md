# Add workflow listing enforcement to CI check

## Problem

Several GitHub Actions workflows (beam_*.yml) in `.github/workflows/` are not listed in the workflows README (`.github/workflows/README.md`). There is no automated check to catch this, so new workflows get added without updating the documentation. This makes it hard for contributors to discover available workflows and their trigger phrases.

Additionally, three lightweight PreCommit jobs (GHA, RAT, Whitespace) are running on `main` runners when they should be using `small` runners to free up resources.

## Expected Behavior

1. The Gradle `check` task in `.github/build.gradle` should validate that every `beam_*` prefixed workflow file is listed in `.github/workflows/README.md`. If a workflow is missing from the README, the check should fail with an error message identifying the missing workflow.

2. All currently unlisted `beam_*` workflows should be added to the appropriate section of `.github/workflows/README.md` (PreCommit, PostCommit, PerformanceTests, LoadTests, or Other). After updating the README, update the documentation to reflect the change.

3. The `runs-on` labels for `beam_PreCommit_GHA.yml`, `beam_PreCommit_RAT.yml`, and `beam_PreCommit_Whitespace.yml` should be changed from `main` to `small`.

## Files to Look At

- `.github/build.gradle` — Gradle check task that validates workflow YAML files
- `.github/workflows/README.md` — Documents all GitHub Actions workflows with trigger phrases and badges
- `.github/workflows/beam_PreCommit_GHA.yml` — GHA pre-commit workflow
- `.github/workflows/beam_PreCommit_RAT.yml` — License header check workflow
- `.github/workflows/beam_PreCommit_Whitespace.yml` — Whitespace check workflow
