# Add documentation links to claude/agents.md

Source: [StanfordVL/BEHAVIOR-1K#2095](https://github.com/StanfordVL/BEHAVIOR-1K/pull/2095)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

FYI in general while testing Claude often still has to be prompted explicitly to use the documentation, otherwise it does not always default to looking it up even if it's quite relevant. But now you can e.g. ask it to follow links to the documentation or look at Omniverse or IsaacSim docs. I initially ran into an issue where it would add an extra `docs/` part to the URL which is why I added the extra sentence at the end, seems like it could be a bit finnicky still.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
