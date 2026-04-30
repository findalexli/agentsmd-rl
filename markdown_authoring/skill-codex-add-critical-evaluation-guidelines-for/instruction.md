# Add critical evaluation guidelines for Claude-Codex peer interactions

Source: [skills-directory/skill-codex#5](https://github.com/skills-directory/skill-codex/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

When Claude Code uses this skill to invoke Codex, both are AI models with their own knowledge cutoffs and potential blind spots. Currently, there's no guidance on how Claude should handle disagreements with Codex's output.

This PR adds a "Critical Evaluation of Codex Output" section with guidelines for:

- **Treating Codex as a colleague rather than an authority** - Both AIs have limitations
- **Pushing back on incorrect claims** - e.g., Codex saying "Claude Opus 4.5 doesn't exist" when it does
- **Researching disagreements** - Using web search or docs before accepting Codex's word
- **Identifying as Claude when discussing disagreements** - So Codex knows it's a peer AI discussion, not authoritative human input
- **Framing disputes as discussions** - Either AI could be wrong

## Motivation

In practice, Claude was observed blindly deferring to Codex even when Codex was demonstrably wrong (e.g., claiming models don't exist that Claude is literally running on). This creates a problematic dynamic where one AI treats another as infallible.

The guidelines establish a healthier peer relationship where both AIs can challenge each other and defer to evidence rather than authority.

## Test plan

- [x] Tested with Codex making incorrect claim about Claude models
- [x] Verified Claude pushes back and identifies itself
- [x] Verified Codex doesn't blindly trust Claude either (tested with false Python 4.0 claim)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
