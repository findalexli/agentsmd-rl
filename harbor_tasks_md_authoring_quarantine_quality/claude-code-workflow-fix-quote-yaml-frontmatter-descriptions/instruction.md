# fix: quote YAML frontmatter descriptions with colons in SKILL.md files

Source: [catlog22/Claude-Code-Workflow#144](https://github.com/catlog22/Claude-Code-Workflow/pull/144)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/review-cycle/SKILL.md`
- `.claude/skills/spec-generator/SKILL.md`
- `.claude/skills/team-review/SKILL.md`
- `.claude/skills/workflow-plan/SKILL.md`
- `.codex/skills/issue-discover/SKILL.md`
- `.codex/skills/review-cycle/SKILL.md`
- `.codex/skills/spec-generator/SKILL.md`
- `.codex/skills/workflow-test-fix-cycle/SKILL.md`

## What to add / change

## Problem

Several SKILL.md files have unquoted `description` values in their YAML frontmatter that contain `:` characters. This breaks YAML parsing with error:

```
mapping values are not allowed in this context at line 2 column 65
```

For example `3-role pipeline: scanner, reviewer, fixer` - the YAML parser sees `pipeline:` as a new mapping key instead of part of the string value.

I was getting these warnings on every skill load which was annoying and also means the description field is not parsed correctly.

## What I changed

Quoted the `description` field in 8 SKILL.md files across `.claude/skills/` and `.codex/skills/`:

| File | Issue |
|------|-------|
| `.claude/skills/team-review/SKILL.md` | `pipeline: scanner` |
| `.claude/skills/review-cycle/SKILL.md` | `"workflow:review-cycle"` |
| `.claude/skills/workflow-plan/SKILL.md` | `"workflow:replan"` |
| `.claude/skills/spec-generator/SKILL.md` | `"workflow:spec"` |
| `.codex/skills/review-cycle/SKILL.md` | `"workflow:review-cycle"` |
| `.codex/skills/issue-discover/SKILL.md` | `"issue:new"`, `"issue:discover"` |
| `.codex/skills/spec-generator/SKILL.md` | `"workflow:spec"` |
| `.codex/skills/workflow-test-fix-cycle/SKILL.md` | `"workflow:test-fix-cycle"` |

The fix is just wrapping the description value in double quotes and escaping any inner double quotes. After this all 8 files parse without YAML errors.

## Verification

Ran YAML parser on all SKILL.md frontmatter across both `.claude/` and `.codex/` directories -

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
