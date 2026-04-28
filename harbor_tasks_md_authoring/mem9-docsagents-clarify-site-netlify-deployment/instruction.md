# docs(AGENTS): clarify site/ Netlify deployment and SKILL.md ownership

Source: [mem9-ai/mem9#86](https://github.com/mem9-ai/mem9/pull/86)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

Add explicit documentation about the `site/` directory and SKILL.md ownership rules.

### Changes
- Update `site/` description in module table: "deployed to Netlify from `main` branch"
- Add `site/public/SKILL.md` and `site/public/beta/SKILL.md` to the file reference table
- Add new **`## site/ — Netlify deployment`** section explaining:
  - `/site/` is auto-deployed to mem9.ai from `main`
  - Production SKILL.md → `site/public/SKILL.md` (served at `https://mem9.ai/SKILL.md`)
  - Beta SKILL.md → `site/public/beta/SKILL.md` (served at `https://mem9.ai/beta/SKILL.md`)
  - Agents should edit these files, not any other copy
  - The removed `clawhub-skill/mem9/SKILL.md` should no longer be edited

### Why
Prevents agents from editing the wrong SKILL.md copy, and makes the Netlify deployment relationship explicit.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
