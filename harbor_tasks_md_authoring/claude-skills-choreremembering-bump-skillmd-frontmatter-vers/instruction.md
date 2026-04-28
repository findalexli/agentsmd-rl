# chore(remembering): bump SKILL.md frontmatter version to 5.7.1

Source: [oaustegard/claude-skills#585](https://github.com/oaustegard/claude-skills/pull/585)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `remembering/SKILL.md`

## What to add / change

## What

Bumps `remembering/SKILL.md` frontmatter `metadata.version` from `5.4.0` → `5.7.1`.

## Why

Frontmatter version is the canonical skill version (per Oskar). It was three minor versions behind CHANGELOG:

- `5.5.0` (TF-IDF index, 2026-03-18) — frontmatter not bumped
- `5.7.0` (refs no auto-supersede, #583) — frontmatter not bumped
- `5.7.1` (boot tz/LOCAL_DATE fix, #584) — frontmatter not bumped

This single-line change catches the canonical version up to current state. Both #583 and #584 should have included this; flagging it now so the omission becomes visible.

## Out of scope

- Other skills with similar drift between frontmatter and CHANGELOG (if any). One skill at a time.
- Adding a CI check that frontmatter version matches CHANGELOG head. Worth doing eventually but separate PR.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
