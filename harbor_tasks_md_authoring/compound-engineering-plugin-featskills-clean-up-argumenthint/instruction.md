# feat(skills): clean up argument-hint across ce:* skills

Source: [EveryInc/compound-engineering-plugin#436](https://github.com/EveryInc/compound-engineering-plugin/pull/436)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md`
- `plugins/compound-engineering/skills/ce-compound/SKILL.md`
- `plugins/compound-engineering/skills/ce-ideate/SKILL.md`
- `plugins/compound-engineering/skills/ce-plan/SKILL.md`
- `plugins/compound-engineering/skills/ce-review/SKILL.md`
- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

The bracket syntax in `argument-hint` was confusing users — square brackets conventionally mean "optional" in CLI man pages, but most people read them as "type something here." Since the core `ce:*` workflow skills all work fine invoked bare, the hints were creating false pressure to provide input.

**Changes by skill:**

| Skill | Before | After |
|-------|--------|-------|
| `ce:review` | `[mode:autofix\|mode:report-only\|mode:headless] [PR number, GitHub URL, or branch name]` | `[blank to review current branch, or provide PR link]` |
| `ce:work` | `[plan file path or description of work to do]` | `[Plan doc path or description of work. Blank to auto use latest plan doc]` |
| `ce:work-beta` | `[plan file path or description of work to do]` | `[Plan doc path or description of work. Blank to auto use latest plan doc]` |
| `ce:plan` | `[feature description, requirements doc path, or improvement idea]` | `[optional: feature description, requirements doc path, or improvement idea]` |
| `ce:ideate` | `[optional: feature, focus area, or constraint]` | `[feature, focus area, or constraint]` |
| `ce:compound` | `[optional: brief context about the fix]` | *(removed)* |
| `ce:compound-refresh` | `[mode:autofix] [optional: scope hint]` | *(removed)* |

---

[![Compound Engineering v2.59.0](https://img.shields.io/badge/Compound_Engineering-v2.59.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, high effort) via [Claude Code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
