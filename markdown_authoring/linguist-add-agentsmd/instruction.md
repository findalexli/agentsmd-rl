# Add `AGENTS.md`

Source: [github-linguist/linguist#7798](https://github.com/github-linguist/linguist/pull/7798)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!--- Briefly describe your changes in the field above. -->

## Description

People are going to use AI to create PRs so lets make their life easier, and ours too, by adding an AGENTS.md file. This will hopefully reduce the amount of slop we're getting and also ensure things like our PR template are used and properly filled in.

This is agent-agnostic so should work for all agents.

## Checklist:

N/A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
