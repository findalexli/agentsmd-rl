# docs: unify CLAUDE.md and AGENTS.md

Source: [cjpais/Handy#1272](https://github.com/cjpais/Handy/pull/1272)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Before Submitting This PR

- [x] I have searched [existing issues](https://github.com/cjpais/Handy/issues) and [pull requests](https://github.com/cjpais/Handy/pulls) (including closed ones) to ensure this isn't a duplicate
- [x] I have read [CONTRIBUTING.md](https://github.com/cjpais/Handy/blob/main/CONTRIBUTING.md)

## Human Written Description

Unified the source prompt for AI agents to eliminate duplication and inconsistencies between CLAUDE.md and AGENTS.md. Merged content from both files into AGENTS.md as the single source of truth. Kept the frontend/backend architecture and other technical descriptions unchanged, as that would require a separate (likely large) review cycle and is better suited for a separate PR. Added explicit links to PR template, contributing guidelines, troubleshooting, and feature request workflow.

## Related Issues/Discussions

N/A

## Testing

Documentation-only change, no runtime impact. Verified that Claude Code reads AGENTS.md content via the `Read @AGENTS.md` directive in CLAUDE.md at agent initialization (loaded into context automatically, not deferred to later reads).

## AI Assistance

- [ ] No AI was used in this PR
- [x] AI was used (please describe below)

**If AI was used:**

- Tools used: Claude Code
- How extensively: AI assisted with merging content from both files, verifying current project structure, and drafting the unified document

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
