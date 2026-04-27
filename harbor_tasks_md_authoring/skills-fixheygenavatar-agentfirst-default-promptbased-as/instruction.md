# fix(heygen-avatar): agent-first default + prompt-based as primary path

Source: [heygen-com/skills#55](https://github.com/heygen-com/skills/pull/55)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `heygen-avatar/SKILL.md`

## What to add / change

## Problem

Follow-up to #51. When a user asked an agent to "set up an avatar," the agent routed to the user as the avatar target (asking for their photo) instead of creating an avatar for the agent itself.

Two remaining bugs:

### Bug 1: Agent defaulted to user on ambiguous requests

Phase 0 routing required "your avatar" / "my avatar" literal phrasing. Ambiguous requests ("create an avatar", "set up an avatar") fell through to the user branch by default. Then Phase 1 ran the conversational user path — asking for a photo instead of reading `IDENTITY.md`.

### Bug 2: Photo framed as default, prompt as fallback

The Reference Photo Nudge fired universally before Phase 2, so even agent avatars (which should use prompt-based creation from `SOUL.md`) got the "give me a headshot" ask. Prompt-based was framed as the escape hatch ("just say skip").

## Fix

### Start Here block
- Explicit "default target = the agent, not the user"
- "Prompt-based is the default creation path. Photo is opt-in"

### Phase 0 (inverted routing priority)
1. **User** (explicit only) — requires possessive pronoun ("my avatar", "me") or explicit photo reference
2. **Named character** (explicit only) — "called X", "named Y"
3. **Agent** (default) — everything else, including ambiguous requests

When in doubt: default to agent. Single clarifying question allowed if still ambiguous after reading `IDENTITY.md`.

### Phase 1
- For agents: proceed directly to Type A (prompt) creation
- For users: real-person dig

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
