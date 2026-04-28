# chore: include `AGENTS.md` file

Source: [cachebag/nmrs#338](https://github.com/cachebag/nmrs/pull/338)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Despite my disdain for AI slop, there's evidently a function for them in some facet.

 More than anything, I'd at least want someone writing slop with a little bit of guidance on how nmrs operates.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
