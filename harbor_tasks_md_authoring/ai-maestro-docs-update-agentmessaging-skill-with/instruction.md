# docs: Update agent-messaging skill with smart lookup & fuzzy matching

Source: [23blocks-OS/ai-maestro#71](https://github.com/23blocks-OS/ai-maestro/pull/71)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/agent-messaging/SKILL.md`

## What to add / change

## Summary
Updates the agent-messaging skill documentation to reflect the new features from v0.17.32 and v0.17.33.

## Changes
- **Parameters section**: Documents smart lookup (no @host needed) and fuzzy matching
- **Examples**: Shows simplified usage without always requiring @host
- **Cross-host workflow**: Updated to explain the new two-phase lookup
- **Troubleshooting**: Improved guidance for "agent not found" errors

Now agents can just use partial/approximate names like:
```bash
send-aimaestro-message.sh api-form "Subject" "Message"
# 🔍 Found partial match: api-forms@hostname
# ✅ Message sent
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
