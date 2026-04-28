# docs: update AGENTS.md

Source: [strands-agents/sdk-typescript#862](https://github.com/strands-agents/sdk-typescript/pull/862)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Description
<!-- Provide a detailed description of the changes in this PR -->

Updated `AGENTS.md` with the udpated directory structure and information regarding new directories: `strands-py`, `strands-wasm`, `strands-dev`.

## Related Issues

<!-- Link to related issues using #issue-number format -->

## Documentation PR

<!-- Link to related associated PR in the agent-docs repo -->

## Type of Change

<!-- Choose one of the following types of changes, delete the rest -->

Documentation update

## Testing

How have you tested the change?

- [x] I ran `npm run check`

## Checklist
- [x] I have read the CONTRIBUTING document
- [x] I have added any necessary tests that prove my fix is effective or my feature works
- [x] I have updated the documentation accordingly
- [x] I have added an appropriate example to the documentation to outline the feature, or no new docs are needed
- [x] My changes generate no new warnings
- [x] Any dependent changes have been merged and published

----

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
