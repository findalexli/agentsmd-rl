# Replace 'ask the user' with AskUserQuestion tool in skills

Source: [qwibitai/nanoclaw#389](https://github.com/qwibitai/nanoclaw/pull/389)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-discord/SKILL.md`
- `.claude/skills/add-gmail/SKILL.md`
- `.claude/skills/add-parallel/SKILL.md`
- `.claude/skills/add-telegram/SKILL.md`
- `.claude/skills/add-voice-transcription/SKILL.md`
- `.claude/skills/setup/SKILL.md`

## What to add / change

## Summary

This PR updates all skill files to use the `AskUserQuestion` tool instead of generic "ask the user" instructions, providing a consistent and structured pattern for collecting user input during skill execution.

## Changes

### Skills Updated

| Skill | Changes |
|-------|---------|
| `add-voice-transcription` | API key prompt now uses `AskUserQuestion` |
| `add-gmail` | Mode selection (Tool/Channel) and channel config questions use `AskUserQuestion` |
| `add-discord` | Mode selection and bot token prompts use `AskUserQuestion` |
| `add-parallel` | API key collection and deep research permission prompts use `AskUserQuestion` |
| `add-telegram` | Mode selection, bot token, and swarm support prompts use `AskUserQuestion` |
| `setup` | Node.js, Docker, and container runtime selection prompts use `AskUserQuestion` |

### Pattern Used

Before:
```markdown
Ask the user:
> How do you want to use Gmail?
> **Option 1:** Tool Mode...
> **Option 2:** Channel Mode...
```

After:
```markdown
AskUserQuestion: How do you want to use Gmail?
- **Tool Mode** - Description...
- **Channel Mode** - Description...
```

## Benefits

1. **Consistency** - All skills use the same pattern for user questions
2. **Clarity** - The `AskUserQuestion` directive is explicit and machine-parseable
3. **Documentation** - Follows the pattern already established in `customize/SKILL.md` and `setup/SKILL.md`

## Testing

- All markdown changes are documentation-only
- No code changes required
- Skills rem

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
