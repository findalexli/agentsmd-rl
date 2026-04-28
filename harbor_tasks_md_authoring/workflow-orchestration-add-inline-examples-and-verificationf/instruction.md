# Add inline examples and verification-failure handling to SKILL.md

Source: [vxcozy/workflow-orchestration#2](https://github.com/vxcozy/workflow-orchestration/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

Expands SKILL.md with the pieces I actually want from the feedback in #1, without the workflow file or unverified frontmatter additions.

## What changed

- **Subagent Strategy** — added an `Agent()` template so the call syntax is inline, no need to guess the shape.
- **Self-Improvement Loop** — inline lessons.md example (kept the `references/lessons-format.md` link for the full template).
- **Verification Before Done** — added "if verification fails → return to plan step and revise before retrying" so the loop is explicit.
- **Task Management Protocol** — split into 8 steps: separated `Verify Results` from `Document Results`, added explicit `Handle Failures` step, added inline `tasks/todo.md` example.

## What I deliberately left out

- `.github/workflows/skill-review.yml` — third-party action pinned to `@main` (supply-chain risk), scoring is proprietary, and a single-file repo doesn't need CI feedback commentary.
- `user-invocable: true` and `triggers:` frontmatter — not part of the agentskills.io spec; would be dead metadata.
- Description format change (`|` block → quoted single-line) — both are valid YAML, no reason to churn.
- Removed "Core Principles" section — kept.
- Removed "Would a staff engineer approve this?" and "Knowing everything I know now, implement the elegant solution" phrasing — kept; those are load-bearing prompts.

Closes the useful half of #1.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
