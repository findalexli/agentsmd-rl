# ref(skills): Restructure distributed Warden skills

Source: [getsentry/warden#268](https://github.com/getsentry/warden/pull/268)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/warden-sweep/SKILL.md`
- `skills/warden-sweep/SOURCES.md`
- `skills/warden-sweep/SPEC.md`
- `skills/warden-sweep/references/issue-phase.md`
- `skills/warden-sweep/references/organize-phase.md`
- `skills/warden-sweep/references/patch-phase.md`
- `skills/warden-sweep/references/resume-and-artifacts.md`
- `skills/warden-sweep/references/scan-phase.md`
- `skills/warden-sweep/references/script-interfaces.md`
- `skills/warden-sweep/references/verify-phase.md`
- `skills/warden/SKILL.md`
- `skills/warden/SOURCES.md`
- `skills/warden/SPEC.md`
- `skills/warden/references/cli-reference.md`
- `skills/warden/references/config-schema.md`
- `skills/warden/references/configuration.md`

## What to add / change

Restructure the distributed Warden skills so their runtime files match the skill reference architecture more closely.

This adds maintenance specs and source inventories for both distributed skills, keeps the main /warden skill focused on CLI/config routing, and turns /warden-sweep from a long monolithic SKILL.md into a phase router with focused references for scan, verify, issue, patch, organize, resume, and script interfaces.

The motivation is to make these shipped skills easier to validate, maintain, and port across host agents without losing the existing sweep workflow behavior.

Validated with the skill-writer strict validator for both distributed skills and git diff whitespace checks.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
