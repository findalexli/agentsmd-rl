# Add AI skills and rename CLAUDE.md to AGENTS.md

Source: [mailpoet/mailpoet#6540](https://github.com/mailpoet/mailpoet/pull/6540)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.ai/skills/creating-pull-requests/SKILL.md`
- `.ai/skills/writing-changelog/SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Description

Add new AI skills for the development workflow and reorganize agent configuration:
- New `writing-changelog` skill that guides through creating changelog entries
- Updated `creating-pull-requests` skill to check for missing changelog before PR creation
- Renamed `CLAUDE.md` to `AGENTS.md` with a `CLAUDE.md` pointer file

## Code review notes

_N/A_

## QA notes

_N/A_

## Linked PRs

_N/A_

## Linked tickets

_N/A_

## After-merge notes

_N/A_

## Screenshots or screencast <!-- if applicable -->

_N/A_

## Tasks

- [ ] I have added a changelog entry (`./do changelog:add --type=<type> --description=<description>`)
- [ ] I followed [best practices](https://codex.wordpress.org/I18n_for_WordPress_Developers) for translations
- [ ] I added sufficient test coverage
- [ ] I embraced TypeScript by either creating new files in TypeScript or converting existing JavaScript files when making changes

## Preview

[Preview in WordPress Playground](https://account.mailpoet.com/playground/new/branch:claude-improvements)

_The latest successful build from `claude-improvements` will be used. If none is available, the link won't work._

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
