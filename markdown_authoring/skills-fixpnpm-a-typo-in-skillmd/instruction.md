# fix(pnpm): a typo in SKILL.md file

Source: [antfu/skills#5](https://github.com/antfu/skills/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/pnpm/SKILL.md`

## What to add / change

<!-- DO NOT IGNORE THE TEMPLATE!

Thank you for contributing!

---

> Please be aware that vibe-coding contributions are **🚫 STRICTLY PROHIBITED**. 
> We are humans behind these open source projects, trying hard to maintain good quality and a healthy community. 
> Not only do vibe-coding contributions pollute the code, but they also drain A LOT of unnecessary energy and time from maintainers and toxify the community and collaboration.
>
> All vibe-coded, AI-generated PRs will be rejected and closed without further notice. In severe cases, your account might be banned organization-wide and reported to GitHub.
>
> **PLEASE SHOW SOME RESPECT** and do not do so.

---

Before submitting the PR, please make sure you do the following:

- Read the [Contributing Guide](https://github.com/antfu/contribute).
- Check that there isn't already a PR that solves the problem the same way to avoid creating a duplicate.
- Provide a description in this PR that addresses **what** the PR is solving and **WHY**, or reference the issue that it solves (e.g. `fixes #123`).
- Ideally, include relevant tests that fail without this PR but pass with it.

-->

- [x] <- Keep this line and put an `x` between the brackts.

### Description

<!-- Please insert your description here and provide especially info about the "what" this PR is solving, and "WHY" -->

Fix a typo in pnpm/SKILL.md file, change `preferrably` to `preferably`.

### Linked Issues

none.

### Additional co

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
