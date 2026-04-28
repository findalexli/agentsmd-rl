# Document Tuist environment variables in AGENTS.md

Source: [RevenueCat/purchases-ios#6689](https://github.com/RevenueCat/purchases-ios/pull/6689)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- Adds a Tuist environment variables reference table to `AGENTS.md`
- Covers all env vars in `Tuist/ProjectDescriptionHelpers/Environment.swift`: `TUIST_RC_REMOTE`, `TUIST_RC_XCODE_PROJECT`, `TUIST_INCLUDE_TEST_DEPENDENCIES`, `TUIST_INCLUDE_XCFRAMEWORK_INSTALLATION_TESTS`, `TUIST_SK_CONFIG_PATH`, `TUIST_RC_API_KEY`, `TUIST_LAUNCH_ARGUMENTS`, `TUIST_SWIFT_CONDITIONS`
- Includes a combined usage example

Follows up on feedback from https://github.com/RevenueCat/purchases-ios/pull/6664#discussion_r3123380266.

## Test plan

- [ ] Review the rendered table in `AGENTS.md`

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk documentation-only change with no impact on build or runtime behavior.
> 
> **Overview**
> Adds a **Tuist environment variables** section to `AGENTS.md`, including a table documenting supported `TUIST_*` flags (dependency mode, test dependency inclusion, XCFramework tests, StoreKit config, API key injection, launch arguments, and Swift compilation conditions) and a combined usage example for `tuist generate`.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit c3755832ee76c45cc670ba27ddcc37b49f215553. Bugbot is set up for automated code reviews on this repo. Configure [here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
