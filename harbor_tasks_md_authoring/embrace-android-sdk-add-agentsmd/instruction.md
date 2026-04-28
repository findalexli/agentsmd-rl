# Add agents.md

Source: [embrace-io/embrace-android-sdk#3081](https://github.com/embrace-io/embrace-android-sdk/pull/3081)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Goal

Adds an https://agents.md/ file (and a claude.md file that will automatically read it). I figured this is worth trying to see if it improves the quality of responses from AI tooling. There's no real objective way to measure this so I guess we can see what results are like?

I asked Claude to generate this agents.md file and then reviewed it myself for inaccuracies. I also added a couple of sections on programming conventions for an SDK. I've also added instructions for this file to get updated when the project materially updates, so hopefully this document will remain more-or-less up-to-date.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
