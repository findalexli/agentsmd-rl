# fix(resolve-pr-feedback): add actionability filter and lower cluster gate to 3+

Source: [EveryInc/compound-engineering-plugin#461](https://github.com/EveryInc/compound-engineering-plugin/pull/461)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/resolve-pr-feedback/SKILL.md`

## What to add / change

The resolve-pr-feedback triage step had no spec'd rule for non-actionable review bodies. When encountering Codex bot review wrapper text, the model improvised a "Codex boilerplate" heuristic to skip them — correct in this case, but unspecified behavior that could misfire on bot feedback that puts substantive content in the review body.

Two fixes:

1. **Actionability filter for PR comments and review bodies** — Triage now explicitly drops items with nothing to fix, answer, or decide (wrapper text, approvals, status badges, CI summaries). This replaces the model's ad-hoc classification with a spec'd rule that covers both bot and human non-actionable comments.

2. **Cluster gate volume threshold lowered from 4+ to 3+** — 67% of bot code reviews across recent PRs had fewer than 4 inline comments, consistently bypassing cluster analysis. Bot reviews are naturally succinct but often thematically related. 3+ catches the common bot pattern while still skipping the 1-2 unrelated nitpick case.

---

[![Compound Engineering v2.59.0](https://img.shields.io/badge/Compound_Engineering-v2.59.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
