# Update branching instructions to be version-agnostic

Source: [dotnet/maui#35066](https://github.com/dotnet/maui/pull/35066)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

<!-- Please let the below note in for people that find this PR -->
> [!NOTE]
> Are you waiting for the changes in this PR to be merged?
> It would be very helpful if you could [test the resulting artifacts](https://github.com/dotnet/maui/wiki/Testing-PR-Builds) from this PR and let us know in a comment if this change resolves your issue. Thank you!

## Description

The branching instructions in `.github/copilot-instructions.md` hardcoded `net10.0` as the feature branch for new APIs. This becomes stale every time a new `netN.0` branch is created (e.g., `net11.0`, `net12.0`).

This PR replaces the hardcoded version with a dynamic convention: **the highest `netN.0` branch is the current feature branch for new features and API changes**. It also includes a discovery command so agents can programmatically find the right branch.

## Changes

- Removed hardcoded `net10.0 branch` line from Key Technologies section
- Updated Feature branches description to explain the "highest netN.0" convention
- Replaced hardcoded `net10.0` in Branching section with version-agnostic pattern and discovery command

## Why

This caused a real issue: during a multi-model code review of PR #34230, the reviewer incorrectly recommended targeting `net10.0` instead of `net11.0` because the instructions said `net10.0`. With this change, the instructions will remain correct as branches evolve.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
