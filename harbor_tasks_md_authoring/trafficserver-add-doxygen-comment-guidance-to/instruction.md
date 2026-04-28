# Add doxygen comment guidance to AGENTS.md

Source: [apache/trafficserver#13112](https://github.com/apache/trafficserver/pull/13112)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This adds a Doxygen Comments section to AGENTS.md describing the conventions agents should follow when documenting code with doxygen style comments.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
