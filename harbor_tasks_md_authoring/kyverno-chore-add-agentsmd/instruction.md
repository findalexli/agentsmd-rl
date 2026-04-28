# chore: add AGENTS.md

Source: [kyverno/kyverno#15215](https://github.com/kyverno/kyverno/pull/15215)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Explanation
This PR adds `AGENTS.md` for the project
<!--
In a couple sentences, explain why this PR is needed and what it addresses. This should be an explanation a non-developer user can understand and covers the "why" question. It should also clearly indicate whether this PR represents an addition, a change, or a fix of existing behavior. This explanation will be used to assist in the release note drafting process.

THIS IS MANDATORY.
-->

## Related issue
Closes #15181 
<!--
Please link the GitHub issue this pull request resolves in the format of `Closes #1234`. If you discussed this change
with a maintainer, please mention her/him using the `@` syntax (e.g. `@JimBugwadia`).

If this change neither resolves an existing issue nor has sign-off from one of the maintainers, there is a
chance substantial changes will be requested or that the changes will be rejected.

You can discuss changes with maintainers in the [Kyverno Slack Channel](https://kubernetes.slack.com/).
-->

## Milestone of this PR
<!--

Add the milestone label by commenting `/milestone 1.2.3`.

-->

## Documentation (required for features)

My PR contains new or altered behavior to Kyverno. 
- [ ] I have sent the draft PR to add or update [the documentation](https://github.com/kyverno/website) and the link is:
  <!-- Uncomment to link to the PR -->
  <!-- https://github.com/kyverno/website/pull/123 -->

## What type of PR is this

<!--

> Uncomment only one ` /kind <>`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
