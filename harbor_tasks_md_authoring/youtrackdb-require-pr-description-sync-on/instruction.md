# Require PR description sync on follow-up commits

Source: [JetBrains/youtrackdb#1000](https://github.com/JetBrains/youtrackdb/pull/1000)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

#### Motivation

Squash-merge in this repo builds the final commit message from the PR title and description, not from individual branch commits. When follow-up commits are pushed to an existing PR without updating the PR metadata, the squashed commit silently loses context about what the later commits changed. Making the expectation explicit in `CLAUDE.md` keeps future squashed commits accurate and reviewable.

#### Summary

- Adds a bullet under **Git Conventions → Pull Requests** stating that every additional commit on an open PR must be accompanied by an update to the PR description (and title if scope changed), since the squashed commit is generated from PR metadata.
- Tightens the wording per Gemini review: the original phrasing repeated information from the adjacent bullet and ran long. Collapsed to a single sentence while preserving the key nuance that individual commit messages are discarded on squash.

#### Test plan

- [ ] Docs-only change — no code or tests affected.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
