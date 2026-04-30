# fix(heygen-avatar): Before You Start block ran user-centric logic before Phase 0

Source: [heygen-com/skills#56](https://github.com/heygen-com/skills/pull/56)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `heygen-avatar/SKILL.md`

## What to add / change

## Problem

Follow-up to #55. After those fixes were merged, agents still asked the user for a headshot on install-flow prompts:

```
Skills installed, MCP connected, gateway restarted. ✓
Now — before I build your avatar and video, let me walk through this one step at a time.
First up: your avatar.
Do you have a headshot or reference photo I can use?
```

Root cause: the `Before You Start (Claude Code only)` block at the top of `heygen-avatar/SKILL.md` ran BEFORE Phase 0 and was framed entirely around user onboarding.

## The buggy block (before this PR)

```
First, fetch the user's existing HeyGen avatars.
...
If the user has no existing avatars, tell them none were found and
offer to create one with a few quick questions.
```

Two problems:
1. It fired before Phase 0's agent-first default could kick in
2. "Offer to create with a few quick questions" is the batch-ask behavior #51 tried to eliminate

By the time Phase 0 evaluated, the agent was already in "ask for a photo" mode.

## Fix

### Before You Start (renamed 'environment detection')

Now just detects OpenClaw vs Claude Code environment. Both paths proceed to Phase 0 next — no avatar fetching, no user-onboarding questions.

Added explicit callout: **"Do NOT fetch HeyGen avatars yet. That's a Phase 0 sub-step."**

### Phase 0

Moved the existing-avatar listing logic here as an **optional** check:
- Only runs when Phase 0 target = **user** AND no `AVATAR-<USER>.md` exists
- Agent and named-character paths skip this enti

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
