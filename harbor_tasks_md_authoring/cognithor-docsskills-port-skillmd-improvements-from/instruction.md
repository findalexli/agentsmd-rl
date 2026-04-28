# docs(skills): port SKILL.md improvements from beta to main

Source: [Alex8791-cyber/cognithor#124](https://github.com/Alex8791-cyber/cognithor/pull/124)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/backup/SKILL.md`
- `skills/gmail_sync/SKILL.md`
- `skills/test/SKILL.md`
- `skills/test_skill/SKILL.md`
- `skills/wetter_abfrage/SKILL.md`

## What to add / change

## Summary

Brings the structured skill docs that landed on `beta` (PR #117 + #123) onto `main`. The 5 `skills/*/SKILL.md` files on main were previously 3-line stubs (`Jarvis Skill: Backup` etc.) — now they have YAML frontmatter + Steps + Error Handling / Troubleshooting tables, all Cognithor-branded.

## Why not merge beta → main directly?

Because `beta` is **1397 commits behind main** (stale release branch from the v0.35 era). A direct merge would potentially revert hundreds of thousands of lines. Instead, this PR cherry-picks only the 5 SKILL.md files that represent the doc improvements.

## Not included

Code files in `skills/` (`skill.py`, `manifest.json`, `test_skill.py`) are **intentionally left alone** — they differ between branches for unrelated historical reasons. Main's versions are canonical (post-rebrand, using `cognithor.*` imports); beta's versions still use the old `jarvis.*` imports.

## Credit

Original content from @rohan-tessl in #117, Cognithor rebrand in #123.

## Test plan

- [x] No Jarvis references remain in the copied files (verified via grep)
- [x] Pure docs change — no code, no tests, no behavior

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
