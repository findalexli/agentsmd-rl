# docs: add AGENTS.md file

Source: [Domain-Connect/Templates#980](https://github.com/Domain-Connect/Templates/pull/980)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

The agents file is supposed to be read by various AI tools.  My attempts is to give a hints in it to Service Providers who are using agents to have greater probability of submitting acceptable merge requests.  Maybe this works, and even if not at least I tried.

Reference: https://agents.md/
CC: Pawel Kowalik <pawel.kowalik@denic.de>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
