# feat: add `ooo publish` skill — Seed to GitHub Issues bridge

Source: [Q00/ouroboros#261](https://github.com/Q00/ouroboros/pull/261)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `skills/help/SKILL.md`
- `skills/publish/SKILL.md`

## What to add / change

## Summary

- Adds `ooo publish` skill that converts Seed specifications into structured GitHub Issues
- Bridges the gap between Ouroboros's solo AI workflow and team-based project management
- Registers the new command in CLAUDE.md and help skill
- Fixes pre-existing CI failure in PM completion tests (missing `backend` arg)

## Motivation

Ouroboros's `Interview → Seed → Run → Evaluate` loop is optimized for solo AI-driven development. But in team settings, plans need:

- **Review** — PM, devs, QA must read and comment on requirements
- **History tracking** — Why was this decision made? (GitHub comment threads)
- **Assignment** — Who owns which task?
- **PR linking** — "Closes #42" traceability

GitHub already provides all of this. `ooo publish` bridges Ouroboros's structured output to GitHub's native issue tracking, without changing the existing workflow.

## What `ooo publish` does

```
ooo interview → ooo seed → ooo publish
```

1. Reads the Seed YAML (from session or file path)
2. Creates an **Epic issue** (PRD role) with goal, constraints, acceptance criteria, ontology
3. Creates **Task issues** (one per implementation unit) with test checklists and pass criteria
4. Links tasks back to the Epic via comments
5. Applies `ouroboros`, `epic`, `task` labels

## Files changed

| File | Change |
|------|--------|
| `skills/publish/SKILL.md` | New skill definition |
| `CLAUDE.md` | Register `ooo publish` command |
| `skills/help/SKILL.md` | A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
