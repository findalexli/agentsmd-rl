# feat: add manifest observability skill

Source: [sickn33/antigravity-awesome-skills#103](https://github.com/sickn33/antigravity-awesome-skills/pull/103)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/manifest/SKILL.md`

## What to add / change

## Summary

Adds the **manifest** skill — an observability plugin setup guide for AI agents.

## What it does

- Walks through a 6-step setup: stop gateway, install plugin, get API key, configure, restart, verify
- Includes troubleshooting table for common errors (missing key, invalid format, connection refused, duplicate OTel)
- Includes safety notes, usage examples, and best practices

## Who uses this

Developers who need visibility into their agent behavior via the [Manifest](https://app.manifest.build) observability platform.

## Validation

- `npm run validate` passes with no critical errors
- Frontmatter `name` matches folder name
- Description under 200 characters

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
