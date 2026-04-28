# feat: migrate cursor rules to agent-agnostic skills

Source: [scalar/scalar#8434](https://github.com/scalar/scalar/pull/8434)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/cloud-agents-starter/SKILL.md`
- `.agents/skills/openapi-glossary/SKILL.md`
- `.agents/skills/tests/SKILL.md`
- `.agents/skills/typescript/SKILL.md`
- `.agents/skills/vue-components/SKILL.md`

## What to add / change

<!-- CURSOR_AGENT_PR_BODY_BEGIN -->
## Problem

The project was using Cursor's legacy `.cursor/rules` format for workspace guidance. This PR migrates these rules to the newer, more flexible `.cursor/skills` format, as requested by the user, for improved organization and future compatibility.

## Solution

- Created new skill directories and `SKILL.md` files for each existing rule (e.g., `typescript`, `tests`, `vue-components`, `openapi-glossary`, `cloud-agents-starter`).
- Converted rule frontmatter (`description`, `globs`, `alwaysApply`) to skill frontmatter (`name`, `description`) while retaining the original instructional content.
- Updated internal path references to point to the new skill locations.
- Removed the old `.cursor/rules/*.mdc` files.

## Checklist

- [x] I explained why the change is needed.
- [ ] I added a changeset. <!-- pnpm changeset -->
- [ ] I added tests.
- [x] I updated the documentation.

[Slack Thread](https://apidocumentation.slack.com/archives/D0AKUDSNVSB/p1773399825886449?thread_ts=1773399825.886449&cid=D0AKUDSNVSB)

<div><a href="https://cursor.com/agents/bc-181626fc-be69-574e-83a3-918192715c21"><picture><source media="(prefers-color-scheme: dark)" srcset="https://cursor.com/assets/images/open-in-web-dark.png"><source media="(prefers-color-scheme: light)" srcset="https://cursor.com/assets/images/open-in-web-light.png"><img alt="Open in Web" width="114" height="28" src="https://cursor.com/assets/images/open-in-web-dark.png"></picture></a>&nbsp;<a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
