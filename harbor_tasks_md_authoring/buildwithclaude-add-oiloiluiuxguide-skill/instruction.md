# Add oiloil-ui-ux-guide skill

Source: [davepoon/buildwithclaude#62](https://github.com/davepoon/buildwithclaude/pull/62)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/oiloil-ui-ux-guide/SKILL.md`

## What to add / change

Adds [oiloil-ui-ux-guide](https://github.com/oil-oil/oiloil-ui-ux-guide) — a modern UI/UX guidance and review skill.

**What it does:**
- `guide` mode: actionable do/don't rules for modern clean UI/UX
- `review` mode: prioritized P0/P1/P2 fix lists with design psychology diagnosis

**Covers:** CRAP, task-first UX, cognitive load, HCI laws (Fitts/Hick/Miller), interaction psychology, and modern minimal style.

Full skill with all references: https://github.com/oil-oil/oiloil-ui-ux-guide
Installable via `npx skills add oil-oil/oiloil-ui-ux-guide`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
