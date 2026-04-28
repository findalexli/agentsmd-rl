# Add additional conventions to AGENTS.MD

Source: [PrairieLearn/PrairieLearn#13508](https://github.com/PrairieLearn/PrairieLearn/pull/13508)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!--

Etiquette and expectations for contributions can be found here:
https://prairielearn.readthedocs.io/en/latest/contributing

-->

# Description

These are some additional rules we want LLMs to follow.

<!--

- Summarize your changes and explain the rationale for making them.
- Include any relevant context from Slack, meetings, or other discussions.
- If this change is resolving a specific issue, include a link to the issue (e.g. "closes #1234").
- If applicable, include screenshots and/or videos.
- Note the level of AI assistance used (i.e. none, specific portions, majority of implementation).

-->

# Testing

None.

<!--

- Share how you tested your changes.
- If you're fixing a bug, explain how to reproduce the original issue.
- If applicable, make sure you've authored unit and/or integration tests.
- If applicable, provide instructions for a reviewer to test the changes for themselves.
- If applicable, mention any accessibility testing that was done.

If you re-test your PR after significant changes, please add a comment to the PR saying so.

Self-reviews with GitHub's review UI are encouraged to point out the following:

- Explanations for code or design decisions that may confuse reviewers.
- Particularly important or core changes.
- Items that may need further discussion.
- Changes that may warrant additional testing.

Thank you for contributing to PrairieLearn!

-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
