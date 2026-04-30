# [release-notes skill] Harvest Co-authored-by trailers from all commits in every PR

Source: [modelcontextprotocol/csharp-sdk#1429](https://github.com/modelcontextprotocol/csharp-sdk/pull/1429)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/prepare-release/SKILL.md`
- `.github/skills/prepare-release/references/categorization.md`
- `.github/skills/publish-release/SKILL.md`

## What to add / change

Update attribution rules in prepare-release and publish-release skills to clarify that Co-authored-by trailers should be harvested from all commits in each PR (not just the merge commit) and for every PR regardless of primary author--not only for Copilot-authored PRs.

This gap was identified while referencing this skill to produce a release-notes skill for the dotnet/extensions repo, and coauthors were not being attributed unless Copilot was the primary author.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
