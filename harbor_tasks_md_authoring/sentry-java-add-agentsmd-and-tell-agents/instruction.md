# Add `AGENTS.md` and tell agents to use `.cursor/skills`

Source: [getsentry/sentry-java#5103](https://github.com/getsentry/sentry-java/pull/5103)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

#skip-changelog

## :scroll: Description
<!--- Describe your changes in detail -->
Add `AGENTS.md` and tell agents to use `.cursor/skills`

Had to be worded rather strictly or otherwise Claude would simply ignore the instructions to both read `AGENTS.md` or cursor skills.

## :bulb: Motivation and Context
<!--- Why is this change required? What problem does it solve? -->
<!--- If it fixes an open issue, please link to the issue here. -->

<!--
* resolves: #1234
* resolves: LIN-1234
-->

## :green_heart: How did you test it?


## :pencil: Checklist
<!--- Put an `x` in the boxes that apply -->

- [ ] I added GH Issue ID _&_ Linear ID
- [ ] I added tests to verify the changes.
- [ ] No new PII added or SDK only sends newly added PII if `sendDefaultPII` is enabled.
- [ ] I updated the docs if needed.
- [ ] I updated the wizard if needed.
- [ ] Review from the native team if needed.
- [ ] No breaking change or entry added to the changelog.
- [ ] No breaking change for hybrid SDKs or communicated to hybrid SDKs.


## :crystal_ball: Next steps

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
