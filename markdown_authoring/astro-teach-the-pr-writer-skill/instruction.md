# Teach the PR writer skill about changesets

Source: [withastro/astro#16060](https://github.com/withastro/astro/pull/16060)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/astro-pr-writer/SKILL.md`

## What to add / change

## Changes

- Adds a `Changesets` section to the `astro-pr-writer` skill covering when changesets are required, file format, bump type rules, and CI restrictions on `major`/`minor` core bumps
- Documents the Astro changeset message writing conventions from https://contribute.docs.astro.build/docs-for-code-changes/changesets/ — verb-first present tense, user-facing framing, and type-specific guidance (patch, minor, breaking)
- Instructs agents to always write the changeset file manually rather than offering the interactive CLI wizard, which agents cannot use
- Adds a self-check item to verify a changeset exists before posting any package-modifying PR

## Testing

- Manual review of the updated skill content against the Astro contribution docs and the existing changeset files in the repo

## Docs

- No docs update needed; this change is to an agent skill, not user-facing Astro documentation.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
