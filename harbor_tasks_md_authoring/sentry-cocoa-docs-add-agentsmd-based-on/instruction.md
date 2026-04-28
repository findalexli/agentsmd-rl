# docs: Add AGENTS.md based on Cursor & Claude rules

Source: [getsentry/sentry-cocoa#6825](https://github.com/getsentry/sentry-cocoa/pull/6825)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/file-filters.mdc`
- `.cursor/rules/github-workflow.mdc`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

[AGENTS.md](https://agents.md/) is the upcoming new standard for documenting instructions for AI agents supported by collaborative efforts across the AI software development ecosystem, including [OpenAI Codex](https://openai.com/codex/), [Amp](https://ampcode.com/), [Jules from Google](https://jules.google/), [Cursor](https://cursor.com/), and [Factory](https://factory.ai/).

Next to merging the existing rules I expanded it with:

- Agent updating the AGENTS.md with new learnings in sessions
- Hints regarding handling of pre-commit issues and compaction
- Usage of [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)

#skip-changelog

Closes #6826

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
