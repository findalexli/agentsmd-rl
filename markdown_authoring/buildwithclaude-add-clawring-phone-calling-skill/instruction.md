# Add clawr.ing phone calling skill

Source: [davepoon/buildwithclaude#70](https://github.com/davepoon/buildwithclaude/pull/70)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/clawring/SKILL.md`

## What to add / change

## Summary

Add clawr.ing, a phone calling skill for OpenClaw that lets AI agents make real outbound phone calls to users. The agent calls the user (not the other way around) for alerts, morning briefings, reminders, and urgent notifications.

## Component Details

- **Name**: clawring
- **Type**: Skill
- **Category**: communication

## Testing

- [x] No overlap with existing components
- [x] Tested functionality
- [x] Follows skill structure from CONTRIBUTING.md

## Examples

1. **Morning briefing**: "Call me every morning at 8am with a summary of my calendar and the news."
2. **Price alert**: "Call me if Bitcoin drops below $50k."
3. **Server monitoring**: "Call me if the server goes down."

## Links

- Website: https://clawr.ing
- ClawHub: https://clawhub.ai/marcospgp/clawring

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
