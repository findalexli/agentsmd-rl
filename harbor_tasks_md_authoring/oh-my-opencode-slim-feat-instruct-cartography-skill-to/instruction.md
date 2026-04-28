# feat: instruct cartography skill to register codemap in AGENTS.md

Source: [alvinunreal/oh-my-opencode-slim#175](https://github.com/alvinunreal/oh-my-opencode-slim/pull/175)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/skills/cartography/SKILL.md`

## What to add / change

## Summary

Adds a Step 5 to the cartography skill workflow that tells agents to add a reference to `codemap.md` in `AGENTS.md`. OpenCode auto-loads `AGENTS.md` into every session, so agents will naturally discover and read the codemap — no runtime hooks or injection needed.

Fixes #159

## Approach

Instead of injecting codemap content into every session via a transform hook (context bloat), this leverages OpenCode's existing `AGENTS.md` auto-loading. The cartography skill already generates the codemap; now it also tells the agent to register it where OpenCode looks for project context.

## What changed

**** — Added Step 5 "Register Codemap in AGENTS.md" with instructions to create or update `AGENTS.md` with a section pointing agents to `codemap.md`.

## Why this over hooks

- Zero runtime overhead — no file reads or message transforms on every session
- No context bloat — agents read the codemap when they need it, not on every first message
- Respects OpenCode conventions — `AGENTS.md` is the intended mechanism for project context
- Simple — a one-line SKILL.md change, no new code

@greptileai

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
