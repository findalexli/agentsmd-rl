# chore(FR-2700): add React topic-level skill guides for Claude Code agents

Source: [lablup/backend.ai-webui#6966](https://github.com/lablup/backend.ai-webui/pull/6966)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/react-async-actions/SKILL.md`
- `.claude/skills/react-component-basics/SKILL.md`
- `.claude/skills/react-form/SKILL.md`
- `.claude/skills/react-hooks-extraction/SKILL.md`
- `.claude/skills/react-layout/SKILL.md`
- `.claude/skills/react-modal-drawer/SKILL.md`
- `.claude/skills/react-relay-table/SKILL.md`
- `.claude/skills/react-suspense-fetching/SKILL.md`
- `.claude/skills/react-url-state/SKILL.md`

## What to add / change

resolves #NNN (FR-MMM)
<!-- replace NNN, MMM with the GitHub issue number and the corresponding Jira issue number. -->

<!--
Please precisely, concisely, and concretely describe what this PR changes, the rationale behind codes,
and how it affects the users and other developers.
-->

**Checklist:** (if applicable)

- [ ] Documentation
- [ ] Minium required manager version
- [ ] Specific setting for review (eg., KB link, endpoint or how to setup)
- [ ] Minimum requirements to check during review
- [ ] Test case(s) to demonstrate the difference of before/after

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
