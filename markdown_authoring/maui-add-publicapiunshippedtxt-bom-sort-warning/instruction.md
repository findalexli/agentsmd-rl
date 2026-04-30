# Add PublicAPI.Unshipped.txt BOM sort warning to Copilot instructions

Source: [dotnet/maui#34327](https://github.com/dotnet/maui/pull/34327)

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

PR #34320 fixed RS0017 analyzer errors caused by `#nullable enable` being sorted to the bottom of 14 Maps `PublicAPI.Unshipped.txt` files. The root cause was a prior Copilot agent session that used `LC_ALL=C sort -u` to resolve merge conflicts — the BOM bytes (`0xEF 0xBB 0xBF`) sort after all ASCII characters, pushing the directive below the API entries.

This updates the Copilot instructions to prevent this from recurring:

- Explains that `#nullable enable` must remain on line 1
- Warns against using plain `sort` on these files (BOM sort ordering)
- Provides a safe conflict resolution script that preserves the header before sorting API entries

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
