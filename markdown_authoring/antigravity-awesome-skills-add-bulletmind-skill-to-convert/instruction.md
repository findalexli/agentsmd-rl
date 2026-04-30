# Add bulletmind skill to convert any input into bullets style data

Source: [sickn33/antigravity-awesome-skills#541](https://github.com/sickn33/antigravity-awesome-skills/pull/541)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/bulletmind/EXAMPLES.md`
- `skills/bulletmind/SKILL.md`

## What to add / change

# Add `bulletmind` Structured Bullet Formatting Skill

## Summary

This PR introduces `bulletmind`, a scoped formatting skill for converting content into strictly hierarchical bullet-based output.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Motivation

- Improve readability of dense or unstructured content.
- Enable consistent note-taking and structured thinking outputs.
- Support multi-level decomposition of ideas without prose drift.
- Provide configurable transformation depth through lite, full, and ultra modes.

## Features

- Bullet-only output with one idea per line.
- Hierarchical nested structure with clear idea relationships.
- Scoped activation through explicit bullet-formatting requests.
- Modes for lite, full, and ultra detail levels.

## How to Trigger

Use requests such as `explain in bullets`, `convert to bullets`, `bulletmind full`, or `bulletmind ultra`.

## Quality Bar Checklist ✅

**All applicable items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`, or `unknown` for legacy/unclassified content).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Limitations**: The skill includes a `## Limitations` (or equiva

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
