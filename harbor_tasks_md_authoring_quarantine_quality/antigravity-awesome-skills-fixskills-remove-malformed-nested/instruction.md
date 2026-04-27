# fix(skills): remove malformed nested code fences in browser-extension…

Source: [sickn33/antigravity-awesome-skills#338](https://github.com/sickn33/antigravity-awesome-skills/pull/338)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/browser-extension-builder/SKILL.md`

## What to add / change

# Pull Request Description

- Fixes three malformed code block sections in `skills/browser-extension-builder/SKILL.md` as reported in issue #335
- Three sections (`Extension Architecture`, `Content Scripts`, `Storage and State`) had their entire markdown content — including sub-headings, tables, and inner code blocks — incorrectly wrapped inside an outer ` ```javascript ` fence
- This caused rendered output to show raw markdown syntax (headings, nested fences) as literal text instead of formatted content
- Fix: removed the 3 erroneous outer opening fences and their duplicate section headings, and the 3 dangling closing fences — 12 lines deleted, no content changed

## Root Cause

The pattern sections used a ```` ```javascript ```` block as a wrapper around what should be free markdown, likely from a copy-paste formatting error in the original skill. Markdown renderers do not support nested code fences.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link

Closes #335

## Quality Bar Checklist

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: Frontmatter unchanged and valid — confirmed with `npm run validate` (`✨ All skills passed validation!`).
- [x] **Risk Label**: No change to `risk:` — existing `unknown` label retained as-is.
- [x] **Triggers**: "When to Use" section unchanged.
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
