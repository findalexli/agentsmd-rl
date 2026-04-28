# chore(skills): add new gram-* skills to CLAUDE.md

Source: [speakeasy-api/gram#2386](https://github.com/speakeasy-api/gram/pull/2386)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Something missed when introducing them. In one session, Claude didn't automatically load the new skills and when prompted why it mentioned it was because they were not in this skills table. In another session asking about best practices after this feedback, Claude said that was not strictly necessary due to auto discovery, but suggested making this change anyways so adding here to cover bases.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
