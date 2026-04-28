# chore: Add AGENTS.md

Source: [mudler/LocalAI#7688](https://github.com/mudler/LocalAI/pull/7688)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

**Description**

Basically this is shared system prompt for agents.

**Notes for Reviewers**


**[Signed commits](../CONTRIBUTING.md#signing-off-on-commits-developer-certificate-of-origin)**
- [x] Yes, I signed my commits.
 
<!--
Thank you for contributing to LocalAI! 

Contributing Conventions
-------------------------

The draft above helps to give a quick overview of your PR.

Remember to remove this comment and to at least:

1. Include descriptive PR titles with [<component-name>] prepended. We use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).
2. Build and test your changes before submitting a PR (`make build`). 
3. Sign your commits
4. **Tag maintainer:** for a quicker response, tag the relevant maintainer (see below).
5. **X/Twitter handle:** we announce bigger features on X/Twitter. If your PR gets announced, and you'd like a mention, we'll gladly shout you out!

By following the community's contribution conventions upfront, the review process will 
be accelerated and your PR merged more quickly.

If no one reviews your PR within a few days, please @-mention @mudler.
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
