# Add correct CI pipeline names to Copilot instructions

Source: [dotnet/maui#34255](https://github.com/dotnet/maui/pull/34255)

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

Adds the current Azure DevOps CI pipeline names to `.github/copilot-instructions.md` so that Copilot agents always reference the correct pipelines:

| Pipeline | Name |
|----------|------|
| Overall CI | `maui-pr` |
| Device Tests | `maui-pr-devicetests` |
| UI Tests | `maui-pr-uitests` |

**Why:** Copilot CLI would wrongfully come up with old pipeline names (e.g., `MAUI-UITests-public`) that it picked up from historical PR comments. Adding the correct names to the instruction file ensures agents use the current pipeline names going forward.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
