# fix(skills): plan is a decision artifact; progress comes from git

Source: [EveryInc/compound-engineering-plugin#666](https://github.com/EveryInc/compound-engineering-plugin/pull/666)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-code-review/SKILL.md`
- `plugins/compound-engineering/skills/ce-plan/SKILL.md`
- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

## Summary

Plan files are now trustworthy decision artifacts at every point in their lifecycle. Reviewing a plan mid-execution shows authored intent, not a half-mutated mix of intent and progress. `ce-work` derives per-unit completion from git commits and uncommitted changes on resume, instead of flipping checkboxes in the plan body. Stale progress after reverts, rebases, or abandoned work is now impossible because there is no state to go stale.

This resolves a design tension surfaced after a community member flagged the third-party `planning-with-files` skill as a possible addition (EveryInc/compound-engineering-plugin#146). The underlying concern, plan state that lies about reality, is addressed by removing state rather than adding a sidecar.

## Role separation

The plan file previously played three roles, and mutating it during execution conflated them.

| Role | Before | After |
|---|---|---|
| Decision artifact | Mutated during execution | Immutable during execution |
| Progress tracker | Plan-body checkboxes | Derived from git and the task tracker |
| Audit record | Last-flipped checkbox state | Git log against the branch |

The final `status: active -> completed` frontmatter flip at shipping is the only plan mutation `ce-work` still performs.

## Key decisions

- **Progress is derived, not stored.** Git is the single source of truth for "what's done." Any stored progress (sidecar files, frontmatter blocks, reconciled state) can drift from reality after reverts, reba

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
