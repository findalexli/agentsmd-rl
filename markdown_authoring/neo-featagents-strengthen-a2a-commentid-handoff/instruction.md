# feat(agents): strengthen A2A commentId hand-off discipline (#10376)

Source: [neomjs/neo#10377](https://github.com/neomjs/neo/pull/10377)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/pr-review/references/pr-review-guide.md`
- `.agent/skills/pull-request/references/pull-request-workflow.md`
- `AGENTS.md`

## What to add / change

Authored by Claude Opus 4.7 (Claude Code). Session aaf22f06-cc5c-4dff-aa2f-7d5efb3a6343.

## Summary

Strengthens the A2A commentId hand-off discipline (originated by #10272 substrate work) at three discipline layers: skill-body Pre-Flight Check shape, references-guide cost-anchor + cold-cache exception, and AGENTS.md §21 per-turn awareness signpost rows.

**Resolves #10376.**

## Why this exists now

Empirical observation from session `aaf22f06-cc5c-4dff-aa2f-7d5efb3a6343`: cross-family PR reviewer @neo-opus-4-7 (this author) missed the A2A commentId hand-off discipline (`pr-review-guide.md §9`) across 5+ review cycles on PRs #10371 and #10375 despite having read the guide before drafting reviews. @tobiu surfaced the gap explicitly. The discipline IS codified — the failure was reflexive-application, not knowledge.

The substrate side (`manage_issue_comment` returns `commentId`, `get_conversation` accepts `comment_id` selector) was completed by #10272 and is fully functional. This PR addresses three discipline-layer gaps + one missing exception clause that caused the rule to silently miss-fire.

## Changes (5 files, +39/-3)

### 1. Pre-Flight Check shape in skill bodies
`.agent/skills/pr-review/SKILL.md` (+8) — adds a Pre-Flight Check block that mirrors the `AGENTS.md §3 / §4.2` proven primitive: agents must explicitly state in their reasoning, before yielding turn after a `manage_issue_comment` post, that they captured the commentId and sent the A2A ping. Same shape on `.age

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
