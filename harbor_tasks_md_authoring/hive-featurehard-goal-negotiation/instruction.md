# Feature/hard goal negotiation

Source: [aden-hive/hive#4270](https://github.com/aden-hive/hive/pull/4270)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/hive-create/SKILL.md`
- `.claude/skills/hive/SKILL.md`

## What to add / change

## Description

closes #4267

Adds a mandatory use-case qualification phase (STEP 2) to the `hive-create` skill that forces the agent builder to conduct honest, structured negotiation with the user **before** any agent design or code is written.

Previously, the skill jumped straight from environment setup to goal definition — users could start building agents for problems the framework isn't suited for, only to discover limitations late. This change front-loads that discovery.

### What changed

**New STEP 2: Qualify the Use Case** — inserted between environment setup and goal definition, with five sub-phases:

- **2a: Deep Discovery** — several example questions covering core purpose, interaction model, and external dependencies. 
- **2b: Capability Assessment** — "The Good, The Bad, The Ugly" framework fit assessment, referencing actual tools discovered in STEP 1.
- **2c: Gap Analysis** — Requirement-by-requirement table showing supported / partial / not supported status with workarounds.
- **2d: Recommendation** — One of three clear verdicts: PROCEED, PROCEED WITH SCOPE ADJUSTMENT, or RECONSIDER (with alternatives).
- **2e: Explicit Acknowledgment** — User must actively choose to proceed, adjust scope, ask questions, or reconsider before building begins.

**New reference section: Framework Capabilities for Qualification** — structured tables the builder uses during STEP 2:

| Section | Contents |
|---------|----------|
| The Good | 8 framework streng

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
