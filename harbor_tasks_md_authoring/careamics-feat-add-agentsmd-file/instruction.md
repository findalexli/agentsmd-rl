# Feat: add AGENTS.md file

Source: [CAREamics/careamics#704](https://github.com/CAREamics/careamics/pull/704)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Description

To best help us and potential contributors to make the best of Claude models when working with the CAREamics code-base, we should add a `CLAUDE.md` file that will guide the LLM into modifying the code while respecting its principles.

Because I am myself not using it extensively with project-wide context, this is better as draft for us to play around. So I just put some thoughts specifically for the next version of CAREamics (what we refer to as `NG CAREamics`, which is based around the `NGDataset`).

Things we could add:
- A section specifically about what we are more likely to accept (e.g. new implementation of one of our protocol, new algorithm that does not alter the code throughout) or not (e.g. support for another data format, features specific for a particular new algorithm but added to all the other algorithms)
- A section stating that the principles behind each module can be found in `__ini__.py`, which is currently not true but could be implemented throughout.
- A section on breaking down modifications into small self-contained PRs. (is this useful?)
    - Ask for a proof of principle in a separated module as first PR? 
    - This is probably relevant as contribution guidelines
- CAREamics API examples.
- docstrings principles.
- Should we break it into several small `Claude.md` files distributed in the various modules? I'd prefer to put the relevant info in the `__init__.py` or a `README.md` since it will be relevant to other LLMs.
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
