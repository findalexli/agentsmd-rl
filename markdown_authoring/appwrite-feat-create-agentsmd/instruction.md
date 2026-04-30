# Feat: Create AGENTS.md

Source: [appwrite/appwrite#10993](https://github.com/appwrite/appwrite/pull/10993)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!--
Thank you for sending the PR! We appreciate you spending the time to work on these changes.

Help us understand your motivation by explaining why you decided to make this change.

You can learn more about contributing to appwrite here: https://github.com/appwrite/appwrite/blob/master/CONTRIBUTING.md

Happy contributing!

-->

## What does this PR do?

Instructs AI to generate best possible code.

## Test Plan

As we use it, we will find out

## Related PRs and Issues

x

## Checklist

- [x] Have you read the [Contributing Guidelines on issues](https://github.com/appwrite/appwrite/blob/master/CONTRIBUTING.md)?
- [x] If the PR includes a change to an API's metadata (desc, label, params, etc.), does it also include updated API specs and example docs?

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
