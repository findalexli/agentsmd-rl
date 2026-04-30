# Explore alternative `AGENTS.md` file

Source: [WordPress/php-ai-client#93](https://github.com/WordPress/php-ai-client/pull/93)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

I researched different `AGENTS.md` structures in other projects and explored a few iterations created by an LLM (I used Gemini CLI) with some guidance on the particular structure).

I'm opening this PR with one that I particularly liked, simply for consideration. 

**I'm not saying that this is holistically particularly better than the current one, but I think it might be helpful for us to compare the different sections.** Maybe there are things we'll want to combine from both variants.

On this note, I would also highly encourage other folks that use a coding agent to explore and share their drafts.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
