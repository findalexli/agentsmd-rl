# Add documentation-writer Claude skill for creating high-quality Kener docs

Source: [rajnandan1/kener#575](https://github.com/rajnandan1/kener/pull/575)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/documentation-writer/SKILL.md`

## What to add / change

Created a specialized Claude skill for writing and editing Kener documentation with emphasis on quality, consistency, and avoiding duplication.

## Implementation

- **Skill file**: `.claude/skills/documentation-writer/SKILL.md`
- **Frontmatter metadata**: Name and description trigger automatic skill invocation when working on documentation
- **Comprehensive guidelines**: Documentation structure, frontmatter requirements, custom heading anchors (`{#anchor-name}`), markdown features, internal linking patterns
- **Duplication prevention**: Explicit guidance to check existing docs and use references instead of duplicating content
- **Quality standards**: Writing style principles, technical writing best practices, complete workflow checklist
- **Common patterns**: Templates for configuration docs, API docs, monitor types with examples from existing docs

## Key Features

**Custom heading anchors**: Documents the critical `{#custom-id}` syntax for stable deep linking across documentation updates

**Navigation integration**: Emphasizes updating `docs.json` when creating new documentation pages

**Quality checklist**: Pre-finalization checklist covering frontmatter, heading IDs, code blocks, tables, links, and navigation entries

**Reference examples**: Points to `email-setup.md`, `api.md`, and `alerting/overview.md` as exemplars

The skill activates automatically when creating or editing files in `src/routes/(docs)/docs/content/` or modifying `docs.json`.

<!-- START COPILOT CODING

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
