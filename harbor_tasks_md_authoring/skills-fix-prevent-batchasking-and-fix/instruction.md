# fix: prevent batch-asking and fix agent onboarding flow

Source: [heygen-com/skills#51](https://github.com/heygen-com/skills/pull/51)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`
- `heygen-avatar/SKILL.md`
- `heygen-video/SKILL.md`

## What to add / change

## Problem

When a user asks an agent to use both skills together ("use heygen-avatar and heygen-video"), the agent fires a 7-item questionnaire upfront instead of walking phases.

**Adam's observed response:**
```
For the avatar:
1. Photo — got a headshot? Photo-based avatars are significantly better than AI-generated ones.
2. Voice — want me to find matching voices or do you have a preference?

For the video:
3. What's it for? 4. Duration? 5. Where's it going? 6. Tone/vibe? 7. Key message?
```

Three bugs:

### 1. Skipped agent-identity path
When the ask was "create your avatar" (for the agent itself), the agent should read `SOUL.md` / `IDENTITY.md` first and extract traits silently. It was jumping straight to "give me a photo."

### 2. Reference photo framed as a gate
SKILL.md says "offer to skip for prompt-based creation" — prompt-based avatars work well. Adam framed it as "photo-based are significantly better than AI-generated," which overstates the SKILL's actual guidance ("better face consistency") and pressures the user into the photo path.

### 3. Batch interrogation
heygen-video's Discovery phase says "Be conversational, skip anything already answered" but Adam fired all 7 items upfront as a structured form.

## Fix

**Prompt-only** changes (no API/behavioral changes):

### SKILL.md (root)
Added UX Rules #5 and #6:
- **#5 Don't batch-ask across skills** — chain triggers run heygen-avatar **then** heygen-video sequentially, not in parallel with one combined questionn

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
