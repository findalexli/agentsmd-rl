# Task: Add major bump support to changeset validation

The `openai-agents-js` repository has a changeset validation system (located in
`.codex/skills/changeset-validation/`) that checks whether version bump levels
in changesets are correct. The system currently supports three bump levels:
`patch`, `minor`, and `none`.

## The problem

The validation system does not recognize `major` as a valid version bump. This
causes two observable failures:

1. **Validation rejects major bumps.** When a changeset validation result contains
   `"required_bump": "major"`, the shape checker rejects it as invalid, and the
   JSON schema does not list `"major"` as an allowed enum value.

2. **Milestone assignment cannot target major versions.** The milestone
   assignment script in the same skill sorts open milestones in **descending**
   order (highest version first) and only selects between patch and minor
   targets. It has no logic for picking a milestone when the required bump is
   `major`.

Additionally, the skill's shared validation prompt (`references/validation-prompt.md`)
and the skill definition (`SKILL.md`) need to document the major bump policy:
major bumps should only be allowed after the first major release; before that,
feature-level changes should not use major bumps.

## Files to work with

All changes are under `.codex/skills/changeset-validation/` and
`.github/codex/schemas/`. The relevant files are:

- A JSON schema file defining the allowed `required_bump` values
- A Node.js script that validates the shape of changeset validation results
- A Node.js script that assigns GitHub milestones based on the required bump level
- A Markdown prompt file that lists validation rules
- A SKILL.md that documents the skill workflow

## What needs to happen

The validation system should accept `"major"` as a valid `required_bump` value
alongside `"patch"`, `"minor"`, and `"none"`. The milestone assignment should
sort milestones in **ascending** order (lowest version first), group them by
major version, and select the next major version's milestone when the required
bump is `"major"`. The validation prompt and skill definition should document
that major bumps are allowed only after the first major release.

## Code Style Requirements

This repository uses ESLint (`eslint.config.mjs`) and Prettier for code style.
Run `pnpm lint` to check your changes. Comments must end with a period.
