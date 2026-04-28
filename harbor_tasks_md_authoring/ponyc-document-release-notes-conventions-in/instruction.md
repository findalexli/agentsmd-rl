# Document release notes conventions in CLAUDE.md

Source: [ponylang/ponyc#5248](https://github.com/ponylang/ponyc/pull/5248)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Context

`CONTRIBUTING.md` explains the changelog label mechanic but does not describe where to put the release notes file or what format to use.

## Changes

Add a Release Notes section to `CLAUDE.md` that points to the `/pony-release-notes` skill if available, with the essential mechanics as a fallback.

## Consequences

Claude knows to create `.release-notes/<slug>.md` per PR rather than editing `next-release.md` directly.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
