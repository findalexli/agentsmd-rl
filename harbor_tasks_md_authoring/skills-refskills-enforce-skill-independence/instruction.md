# ref(skills): Enforce skill independence

Source: [getsentry/skills#127](https://github.com/getsentry/skills/pull/127)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/commit/SKILL.md`
- `skills/pr-writer/SKILL.md`
- `skills/skill-writer/EVAL.md`
- `skills/skill-writer/references/design-principles.md`

## What to add / change

Remove named cross-skill invocations from the `commit` and `pr-writer` skills, and add an Independence principle to `skill-writer/references/design-principles.md` so future skills are authored the same way.

**Why.** Skills that name another skill in their runtime instructions silently break in three ways: the named skill may not be installed, it may be renamed, or it may be overridden by a user's own skill of the same name. `commit` pointed at `create-branch`; `pr-writer` pointed at `sentry-skills:commit`. Both now state the intent directly and trust skill discovery to pick up whatever matches.

**Scope of the principle.** The rule targets *runtime dependency*: agent-facing instructions and loaded resources must not assume another skill is present. Non-runtime mentions — provenance logs, audit allowlists, human-facing eval prompts — are fine. `claude-settings-audit` enumerates every skill name because that is its job, and `prompt-optimizer/SOURCES.md` cites `skill-writer` as a synthesis source; both are intentional exceptions carved out in the principle's text.

**What changed.**
- `skills/commit/SKILL.md` — drop `create-branch` references; keep the "branch off main/master first" requirement inline.
- `skills/pr-writer/SKILL.md` — drop `sentry-skills:commit` references; keep the "commit first" requirement inline.
- `skills/skill-writer/references/design-principles.md` — add an Independence section with do/don't examples and the runtime-scope carve-out.
- `skills/skill-writer

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
