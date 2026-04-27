# Use absolute paths for bin/ scripts — confirmed working

Source: [garagon/nanostack#69](https://github.com/garagon/nanostack/pull/69)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `compound/SKILL.md`
- `plan/SKILL.md`
- `qa/SKILL.md`
- `review/SKILL.md`
- `security/SKILL.md`
- `ship/SKILL.md`
- `think/SKILL.md`

## What to add / change

## Summary

Root cause confirmed via direct testing from the project directory:

```
$ cd ~/labs/nano
$ bin/save-artifact.sh think '...'
→ no such file or directory (exit 127)

$ ~/.claude/skills/nanostack/bin/save-artifact.sh think '...'
→ artifact saved (exit 0)
```

Relative paths never worked from user project directories. The world clock sprint that appeared to work used a different execution path internally.

All 7 SKILL.md files now use `~/.claude/skills/nanostack/bin/` for every script call. Requires `Bash(~/.claude/skills/nanostack/bin/*:*)` in `.claude/settings.json` (added by `init-project.sh` in PR #66).

## Test plan

- [x] `~/.claude/skills/nanostack/bin/save-artifact.sh` saves artifact from project dir
- [x] `~/.claude/skills/nanostack/bin/find-artifact.sh` finds it
- [x] Integrity checksum present
- [x] All 7 SKILL.md files use absolute paths

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
